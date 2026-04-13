import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.agents.graph import build_graph
from app.agents.state import MarketAnalysisState, create_initial_state
from app.api.deps import get_settings, get_supabase
from app.config import Settings
from app.models.market import EconomicIndicator, MarketIndex, Sector
from app.models.news import NewsArticle
from app.services.supabase import SupabaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


def _persist_results(result: MarketAnalysisState, svc: SupabaseService, batch_type: str = "manual") -> dict:
    """Save pipeline results to Supabase."""
    saved = {"indices": 0, "sectors": 0, "news": 0, "regime": False, "scoreboards": 0}
    now_str = datetime.utcnow().isoformat() + "Z"

    market_data = result.get("market_data")
    if market_data:
        import math
        for idx in market_data.indices:
            try:
                price = idx.get("close", idx.get("price", 0))
                change = idx.get("change_p", idx.get("change_percent", 0))
                if not isinstance(price, (int, float)) or math.isnan(price):
                    price = 0
                if not isinstance(change, (int, float)) or math.isnan(change):
                    change = 0
                svc.insert_market_index(MarketIndex(
                    symbol=idx.get("symbol", ""),
                    name=idx.get("name", ""),
                    price=price,
                    change_percent=change,
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

        # Save sector history & stocks
        if market_data.sector_history:
            try:
                cnt = svc.upsert_sector_history(market_data.sector_history)
                saved["sector_history"] = cnt
            except Exception as e:
                logger.warning("Failed to save sector history: %s", e)

        logger.info("sector_stocks count from pipeline: %d", len(market_data.sector_stocks))
        if market_data.sector_stocks:
            try:
                cnt = svc.upsert_sector_stocks(market_data.sector_stocks)
                saved["sector_stocks"] = cnt
                logger.info("Saved %d sector stocks to DB", cnt)
            except Exception as e:
                logger.warning("Failed to save sector stocks: %s", e)

    news_data = result.get("news_data")
    if news_data:
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

        # Save AI-analyzed summaries
        if news_data.article_summaries:
            try:
                summaries_rows = [
                    {**s, "batch_type": batch_type, "analyzed_at": now_str}
                    for s in news_data.article_summaries
                ]
                cnt = svc.upsert_news_summaries(summaries_rows)
                saved["news_summaries"] = cnt
                logger.info("Saved %d news summaries to DB", cnt)
            except Exception as e:
                logger.warning("Failed to save news summaries: %s", e)

        # Save global crises
        if news_data.global_crises:
            try:
                allowed_keys = {"title", "source", "summary", "impact_score", "affected_sector", "sentiment"}
                crises_rows = [
                    {**{k: v for k, v in c.items() if k in allowed_keys}, "batch_type": batch_type, "analyzed_at": now_str}
                    for c in news_data.global_crises
                ]
                cnt = svc.upsert_global_crises(crises_rows)
                saved["global_crises"] = cnt
                logger.info("Saved %d global crises to DB", cnt)
            except Exception as e:
                logger.warning("Failed to save global crises: %s", e)

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
                # Map fields to DB columns
                db_sig = {
                    "signal_type": sig.get("signal_type", "regime_shift"),
                    "signal_grade": sig.get("signal_grade", "WATCH"),
                    "from_sector": sig.get("from_sector"),
                    "to_sector": sig.get("to_sector"),
                    "strength": float(sig.get("strength", 0)),
                    "base_score": float(sig.get("base_score", 0)) if sig.get("base_score") is not None else None,
                    "override_adjustment": float(sig.get("override_adjustment", 0)) if sig.get("override_adjustment") is not None else None,
                    "final_score": float(sig.get("final_score", 0)),
                    "confidence_score": float(sig.get("confidence_score", 0.5)),
                    "macro_environment": sig.get("macro_environment", ""),
                    "reasoning": sig.get("reasoning", ""),
                    "supporting_news_urls": sig.get("supporting_news_urls", []),
                    "batch_type": sig.get("batch_type", batch_type),
                    "detected_at": sig.get("detected_at", now_str),
                }
                svc.client.table("rotation_signals").insert(db_sig).execute()
                saved["signals"] = saved.get("signals", 0) + 1
            except Exception as e:
                logger.warning("Failed to save signal: %s — data: %s", e, sig)

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
        saved = _persist_results(result, svc, batch_type=batch_type)
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


# ---------------------------------------------------------------------------
# 분할 트리거: /trigger/data, /trigger/news, /trigger/analyze
# ---------------------------------------------------------------------------

def _verify_api_key(x_api_key: str, settings: Settings) -> None:
    if not settings.trigger_api_key or x_api_key != settings.trigger_api_key:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/trigger/data")
async def trigger_data(
    x_api_key: str = Header(..., alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
):
    """Data Agent만 실행: Yahoo Finance 시장/섹터 데이터 수집 → DB 저장."""
    _verify_api_key(x_api_key, settings)
    try:
        from app.agents.data_agent import data_agent_node
        from app.agents.state import MarketAnalysisState, create_initial_state

        state = create_initial_state("data_trigger")
        result = await data_agent_node(state, {"configurable": {"settings": settings}})
        market_data = result.get("market_data")

        svc = SupabaseService(settings)
        saved = _persist_market_data(market_data, svc)
        logger.info("trigger/data saved: %s", saved)
        return {"status": "completed", "stage": "data", "saved": saved}
    except Exception as e:
        logger.exception("trigger/data failed")
        raise HTTPException(status_code=500, detail=f"Data pipeline failed: {e}")


@router.post("/trigger/news")
async def trigger_news(
    x_api_key: str = Header(..., alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
):
    """News Agent만 실행: 뉴스 수집 + AI 분석 → DB 저장."""
    _verify_api_key(x_api_key, settings)
    try:
        from app.agents.news_agent import news_agent_node
        from app.agents.state import create_initial_state

        state = create_initial_state("news_trigger")
        result = await news_agent_node(state, {"configurable": {"settings": settings}})
        news_data = result.get("news_data")

        svc = SupabaseService(settings)
        saved = _persist_news_data(news_data, svc, batch_type="news_trigger")
        logger.info("trigger/news saved: %s", saved)
        return {"status": "completed", "stage": "news", "saved": saved}
    except Exception as e:
        logger.exception("trigger/news failed")
        raise HTTPException(status_code=500, detail=f"News pipeline failed: {e}")


@router.post("/trigger/analyze")
async def trigger_analyze(
    x_api_key: str = Header(..., alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
):
    """Analyst Agent만 실행: DB에서 최신 data+news 읽어서 AI 분석 → DB 저장."""
    _verify_api_key(x_api_key, settings)
    try:
        from app.agents.analyst_agent import analyst_agent_node
        from app.agents.state import MarketAnalysisState, MarketData, NewsData

        svc = SupabaseService(settings)

        # DB에서 최신 시장 데이터 로드
        indices = svc.get_latest_indices()
        sectors = svc.get_latest_sectors()
        indicators = svc.get_latest_economic_indicators()

        # 모멘텀/RS를 sectors 행에서 복원
        momentum: dict[str, dict] = {}
        relative_strength: dict[str, float] = {}
        for sec in sectors:
            sym = sec.get("etf_symbol", "")
            momentum[sym] = {
                "momentum_1w": sec.get("momentum_1w", 0),
                "momentum_1m": sec.get("momentum_1m", 0),
                "momentum_3m": sec.get("momentum_3m", 0),
                "momentum_6m": sec.get("momentum_6m", 0),
                "momentum_1y": sec.get("momentum_1y", 0),
            }
            relative_strength[sym] = sec.get("relative_strength", 0.0) or 0.0

        market_data = MarketData(
            indices=indices,
            sectors=sectors,
            economic_indicators=indicators,
            momentum=momentum,
            relative_strength=relative_strength,
        )

        # DB에서 최신 뉴스 로드
        articles = svc.get_latest_news_articles(limit=40)
        articles_by_category: dict[str, list[dict]] = {}
        for a in articles:
            cat = a.get("category", "general")
            articles_by_category.setdefault(cat, []).append(a)

        news_data = NewsData(
            articles_by_category=articles_by_category,
        )

        # Analyst Agent 실행
        state: MarketAnalysisState = {
            "batch_type": "analyze_trigger",
            "triggered_at": datetime.utcnow().isoformat() + "Z",
            "market_data": market_data,
            "news_data": news_data,
            "news_fallback_used": False,
            "analysis_results": None,
        }
        result = await analyst_agent_node(state, {"configurable": {"settings": settings}})
        analysis = result.get("analysis_results")

        # 분석 결과 DB 저장
        saved = _persist_analysis(analysis, svc, batch_type="analyze_trigger")
        logger.info("trigger/analyze saved: %s", saved)
        return {"status": "completed", "stage": "analyze", "saved": saved}
    except Exception as e:
        logger.exception("trigger/analyze failed")
        raise HTTPException(status_code=500, detail=f"Analyze pipeline failed: {e}")


# ---------------------------------------------------------------------------
# 분할 저장 헬퍼
# ---------------------------------------------------------------------------

def _persist_market_data(market_data, svc: SupabaseService) -> dict:
    """Data Agent 결과만 DB에 저장."""
    saved: dict[str, int] = {"indices": 0, "sectors": 0, "indicators": 0}
    if not market_data:
        return saved
    now_str = datetime.utcnow().isoformat() + "Z"

    import math
    for idx in market_data.indices:
        try:
            price = idx.get("close", idx.get("price", 0))
            change = idx.get("change_p", idx.get("change_percent", 0))
            if not isinstance(price, (int, float)) or math.isnan(price):
                price = 0
            if not isinstance(change, (int, float)) or math.isnan(change):
                change = 0
            svc.insert_market_index(MarketIndex(
                symbol=idx.get("symbol", ""),
                name=idx.get("name", ""),
                price=price,
                change_percent=change,
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

    if market_data.sector_history:
        try:
            cnt = svc.upsert_sector_history(market_data.sector_history)
            saved["sector_history"] = cnt
        except Exception as e:
            logger.warning("Failed to save sector history: %s", e)

    if market_data.sector_stocks:
        try:
            cnt = svc.upsert_sector_stocks(market_data.sector_stocks)
            saved["sector_stocks"] = cnt
        except Exception as e:
            logger.warning("Failed to save sector stocks: %s", e)

    return saved


def _persist_news_data(news_data, svc: SupabaseService, batch_type: str = "manual") -> dict:
    """News Agent 결과만 DB에 저장."""
    saved: dict[str, int] = {"news": 0}
    if not news_data:
        return saved
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

    if news_data.article_summaries:
        try:
            summaries_rows = [
                {**s, "batch_type": batch_type, "analyzed_at": now_str}
                for s in news_data.article_summaries
            ]
            cnt = svc.upsert_news_summaries(summaries_rows)
            saved["news_summaries"] = cnt
        except Exception as e:
            logger.warning("Failed to save news summaries: %s", e)

    if news_data.global_crises:
        try:
            allowed_keys = {"title", "source", "summary", "impact_score", "affected_sector", "sentiment"}
            crises_rows = [
                {**{k: v for k, v in c.items() if k in allowed_keys}, "batch_type": batch_type, "analyzed_at": now_str}
                for c in news_data.global_crises
            ]
            cnt = svc.upsert_global_crises(crises_rows)
            saved["global_crises"] = cnt
        except Exception as e:
            logger.warning("Failed to save global crises: %s", e)

    return saved


def _persist_analysis(analysis, svc: SupabaseService, batch_type: str = "manual") -> dict:
    """Analyst Agent 결과만 DB에 저장."""
    saved: dict[str, int] = {"regime": 0, "scoreboards": 0, "signals": 0}
    if not analysis:
        return saved

    if analysis.regime:
        try:
            svc.client.table("macro_regimes").insert(analysis.regime).execute()
            saved["regime"] = 1
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
            db_sig = {
                "signal_type": sig.get("signal_type", "regime_shift"),
                "signal_grade": sig.get("signal_grade", "WATCH"),
                "from_sector": sig.get("from_sector"),
                "to_sector": sig.get("to_sector"),
                "strength": float(sig.get("strength", 0)),
                "base_score": float(sig.get("base_score", 0)) if sig.get("base_score") is not None else None,
                "override_adjustment": float(sig.get("override_adjustment", 0)) if sig.get("override_adjustment") is not None else None,
                "final_score": float(sig.get("final_score", 0)),
                "confidence_score": float(sig.get("confidence_score", 0.5)),
                "macro_environment": sig.get("macro_environment", ""),
                "reasoning": sig.get("reasoning", ""),
                "supporting_news_urls": sig.get("supporting_news_urls", []),
                "batch_type": sig.get("batch_type", batch_type),
                "detected_at": sig.get("detected_at", datetime.utcnow().isoformat() + "Z"),
            }
            svc.client.table("rotation_signals").insert(db_sig).execute()
            saved["signals"] += 1
        except Exception as e:
            logger.warning("Failed to save signal: %s — data: %s", e, sig)

    if analysis.report:
        try:
            svc.client.table("market_reports").insert(analysis.report).execute()
            saved["report"] = 1
        except Exception as e:
            logger.warning("Failed to save report: %s", e)

    return saved
