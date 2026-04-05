import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.agents.graph import build_graph
from app.agents.state import MarketAnalysisState, create_initial_state
from app.api.deps import get_settings, get_supabase
from app.config import Settings
from app.models.market import MarketIndex, Sector
from app.models.news import NewsArticle
from app.services.supabase import SupabaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


def _persist_results(result: MarketAnalysisState, svc: SupabaseService) -> dict:
    """Save pipeline results to Supabase."""
    saved = {"indices": 0, "sectors": 0, "news": 0, "regime": False, "scoreboards": 0}

    market_data = result.get("market_data")
    if market_data:
        now_str = datetime.utcnow().isoformat() + "Z"
        for idx in market_data.indices:
            try:
                svc.insert_market_index(MarketIndex(
                    symbol=idx.get("symbol", ""),
                    name=idx.get("name", ""),
                    price=idx.get("close", idx.get("price", 0)),
                    change_percent=idx.get("change_p", idx.get("change_percent", 0)),
                    collected_at=now_str,
                ))
                saved["indices"] += 1
            except Exception as e:
                logger.warning("Failed to save index: %s", e)

        for sec in market_data.sectors:
            try:
                mom = market_data.momentum.get(sec.get("symbol", ""), {})
                svc.insert_sector(Sector(
                    name=sec.get("name", sec.get("symbol", "")),
                    etf_symbol=sec.get("symbol", ""),
                    price=sec.get("close", sec.get("price", 0)),
                    change_percent=sec.get("change_p", sec.get("change_percent", 0)),
                    volume=sec.get("volume", 0),
                    momentum_1w=mom.get("momentum_1w"),
                    momentum_1m=mom.get("momentum_1m"),
                    momentum_3m=mom.get("momentum_3m"),
                    momentum_6m=mom.get("momentum_6m"),
                    momentum_1y=mom.get("momentum_1y"),
                    week_52_low=sec.get("week_52_low"),
                    week_52_high=sec.get("week_52_high"),
                    relative_strength=market_data.relative_strength.get(sec.get("symbol", "")),
                    collected_at=now_str,
                ))
                saved["sectors"] += 1
            except Exception as e:
                logger.warning("Failed to save sector: %s", e)

        for ind in market_data.economic_indicators:
            try:
                svc.insert_economic_indicator(EconomicIndicator(
                    indicator_name=ind["indicator_name"],
                    value=ind["value"],
                    previous_value=ind.get("previous_value"),
                    change_direction=ind.get("change_direction", "flat"),
                    source=ind.get("source", "EODHD"),
                    reported_at=now_str,
                ))
                saved["indicators"] = saved.get("indicators", 0) + 1
            except Exception as e:
                logger.warning("Failed to save indicator: %s", e)

    news_data = result.get("news_data")
    if news_data:
        now_str = datetime.utcnow().isoformat() + "Z"
        for category_key, articles in news_data.articles_by_category.items():
            for a in articles:
                try:
                    svc.insert_news_article(NewsArticle(
                        category=category_key,
                        title=a.get("title", ""),
                        source=a.get("source", {}).get("name", "") if isinstance(a.get("source"), dict) else str(a.get("source", "")),
                        url=a.get("url", ""),
                        summary=a.get("description"),
                        published_at=a.get("publishedAt", now_str),
                        collected_at=now_str,
                    ))
                    saved["news"] += 1
                except Exception as e:
                    logger.warning("Failed to save news: %s", e)

    analysis = result.get("analysis_results")
    if analysis:
        if analysis.regime:
            try:
                svc.client.table("macro_regimes").insert(analysis.regime).execute()
                saved["regime"] = True
            except Exception as e:
                logger.warning("Failed to save regime: %s", e)

        for sb in analysis.scoreboards:
            try:
                svc.client.table("sector_scoreboards").insert(sb).execute()
                saved["scoreboards"] += 1
            except Exception as e:
                logger.warning("Failed to save scoreboard: %s", e)

        for sig in analysis.rotation_signals:
            try:
                svc.client.table("rotation_signals").insert(sig).execute()
            except Exception as e:
                logger.warning("Failed to save signal: %s", e)

        if analysis.report:
            try:
                svc.client.table("market_reports").insert(analysis.report).execute()
            except Exception as e:
                logger.warning("Failed to save report: %s", e)

    return saved


async def run_pipeline(batch_type: str = "manual") -> dict:
    graph = build_graph()
    initial_state = create_initial_state(batch_type)
    result = await graph.ainvoke(initial_state)

    # Persist to Supabase
    try:
        svc = SupabaseService(Settings())
        saved = _persist_results(result, svc)
        logger.info("Pipeline results saved: %s", saved)
    except Exception as e:
        logger.error("Failed to persist results: %s", e)
        saved = {}

    return {"status": "completed", "batch_type": batch_type, "saved": saved}


@router.get("/report")
def get_report(svc: SupabaseService = Depends(get_supabase)):
    report = svc.get_latest_report()
    if report is None:
        raise HTTPException(status_code=404, detail="No report available")
    return report


@router.get("/scoreboards")
def get_scoreboards(
    batch_type: str | None = Query(None, description="Batch type filter (optional)"),
    svc: SupabaseService = Depends(get_supabase),
):
    if batch_type:
        return svc.get_latest_scoreboards(batch_type)
    # No filter: return most recent scoreboards regardless of batch_type
    result = (
        svc.client.table("sector_scoreboards")
        .select("*")
        .order("scored_at", desc=True)
        .limit(12)
        .execute()
    )
    return result.data


@router.get("/signals")
def get_rotation_signals(svc: SupabaseService = Depends(get_supabase)):
    return svc.get_latest_rotation_signals()


@router.post("/trigger")
async def trigger_pipeline(
    x_api_key: str = Header(..., alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
):
    if not settings.trigger_api_key or x_api_key != settings.trigger_api_key:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        result = await run_pipeline("manual")
        return result
    except Exception as e:
        logger.exception("Pipeline trigger failed")
        raise HTTPException(status_code=500, detail="Pipeline execution failed")
