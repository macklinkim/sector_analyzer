# backend/app/agents/analyst_agent.py
import json
import logging
from datetime import datetime, timezone

import anthropic
from langchain_core.runnables import RunnableConfig

from app.agents.state import MarketAnalysisState, AnalysisResults
from app.config import Settings
from app.services.supabase import SupabaseService

logger = logging.getLogger(__name__)

REGIME_DETECTION_PROMPT = """You are a macro-economic analyst. Based on the market data and news below, determine the current macro regime.

## Macro Regime Matrix (2D)
- **Goldilocks**: High Growth + Low Inflation — bull market, risk-on
- **Reflation**: High Growth + High Inflation — overheating, commodity demand
- **Stagflation**: Low Growth + High Inflation — cost push, worst market
- **Deflation**: Low Growth + Low Inflation — recession, safe haven

## Market Data
{market_data}

## News Summary
{news_summary}

## Sector Regime Mapping
{sector_mapping}

Respond with ONLY valid JSON (no markdown, no explanation):
{{"regime": "goldilocks|reflation|stagflation|deflation", "growth_direction": "high|low", "inflation_direction": "high|low", "regime_probabilities": {{"goldilocks": 0.0, "reflation": 0.0, "stagflation": 0.0, "deflation": 0.0}}, "reasoning": "explanation in Korean"}}"""

SCORING_PROMPT = """You are a sector rotation analyst. Given the detected macro regime and market context, score each sector.

## Current Regime
{regime_json}

## Sector Mapping with Override Rules
{sector_mapping}

## Market Momentum Data
{momentum_data}

## News by Category
{news_data}

## Scoring Formula
Final Score = (Base Score x Regime Confidence) + Override Adjustment + (News Sentiment x 0.2) + (Momentum x 0.15)
- Base Score: favorable regime = +0.6, unfavorable = -0.4, neutral = 0.0
- Override: check override_rules triggers against news, apply if matched (-0.5 ~ +0.5)
- Recommendation: >= +0.5 overweight, -0.2 ~ +0.5 neutral, < -0.2 underweight

Respond with ONLY valid JSON (no markdown):
{{"scoreboards": [{{"sector_name": "...", "etf_symbol": "...", "base_score": "0.0", "override_score": "0.0", "news_sentiment_score": "0.0", "momentum_score": "0.0", "final_score": "0.0", "rank": 1, "recommendation": "overweight|neutral|underweight", "reasoning": "explanation in Korean"}}], "rotation_signals": [{{"signal_type": "rotation_in|rotation_out|regime_shift", "from_sector": "...", "to_sector": "...", "strength": "0.0", "final_score": "0.0", "reasoning": "explanation in Korean"}}], "report_summary": "overall market summary in Korean", "key_highlights": ["point 1", "point 2", "point 3"]}}"""


async def analyst_agent_node(state: MarketAnalysisState, config: RunnableConfig) -> dict:
    """LangGraph node: analyze market data + news using Claude API."""
    logger.info("Analyst Agent: starting analysis (batch=%s)", state["batch_type"])

    try:
        settings = config.get("configurable", {}).get("settings")
    except Exception:
        settings = None
    if settings is None:
        settings = Settings()

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Load sector mapping
    try:
        supa = SupabaseService(settings)
        sector_mapping = supa.get_sector_mapping()
    except Exception as e:
        logger.warning("Failed to load sector mapping: %s", e)
        sector_mapping = []

    market_data = state.get("market_data")
    news_data = state.get("news_data")
    batch_type = state["batch_type"]
    now = datetime.now(timezone.utc)

    # Format data for prompts
    market_summary = json.dumps({
        "indices": market_data.indices if market_data else [],
        "sectors": market_data.sectors if market_data else [],
    }, default=str, ensure_ascii=False)

    news_summary = ""
    if news_data:
        for cat, articles in news_data.articles_by_category.items():
            news_summary += f"\n### {cat}\n"
            for a in articles[:3]:
                title = a.get("title", "")
                desc = a.get("description", "")
                news_summary += f"- {title}: {desc}\n"

    mapping_str = json.dumps(sector_mapping, default=str, ensure_ascii=False)
    momentum_str = json.dumps(market_data.momentum if market_data else {}, default=str)

    # Step 1: Macro Regime Detection
    regime_prompt = REGIME_DETECTION_PROMPT.format(
        market_data=market_summary, news_summary=news_summary, sector_mapping=mapping_str,
    )

    try:
        regime_response = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=1024,
            messages=[{"role": "user", "content": regime_prompt}],
        )
        regime_text = regime_response.content[0].text
        regime_data = json.loads(regime_text)
    except Exception as e:
        logger.error("Regime detection failed: %s", e)
        regime_data = {
            "regime": "goldilocks", "growth_direction": "high", "inflation_direction": "low",
            "regime_probabilities": {"goldilocks": 0.25, "reflation": 0.25, "stagflation": 0.25, "deflation": 0.25},
            "reasoning": "분석 실패 - 기본값 사용",
        }

    regime_data["batch_type"] = batch_type
    regime_data["analyzed_at"] = now.isoformat()

    # Steps 2-4: Scoring & Reporting
    scoring_prompt = SCORING_PROMPT.format(
        regime_json=json.dumps(regime_data, ensure_ascii=False),
        sector_mapping=mapping_str, momentum_data=momentum_str, news_data=news_summary,
    )

    try:
        scoring_response = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=4096,
            messages=[{"role": "user", "content": scoring_prompt}],
        )
        scoring_text = scoring_response.content[0].text
        scoring_data = json.loads(scoring_text)
    except Exception as e:
        logger.error("Scoring failed: %s", e)
        scoring_data = {"scoreboards": [], "rotation_signals": [], "report_summary": "분석 실패", "key_highlights": []}

    for sb in scoring_data.get("scoreboards", []):
        sb["batch_type"] = batch_type
        sb["scored_at"] = now.isoformat()
    for sig in scoring_data.get("rotation_signals", []):
        sig["batch_type"] = batch_type
        sig["detected_at"] = now.isoformat()

    report = {
        "batch_type": batch_type,
        "summary": scoring_data.get("report_summary", ""),
        "key_highlights": scoring_data.get("key_highlights", []),
        "report_date": now.strftime("%Y-%m-%d"),
        "analyzed_at": now.isoformat(),
        "disclaimer": "본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다.",
    }

    analysis_results = AnalysisResults(
        regime=regime_data,
        scoreboards=scoring_data.get("scoreboards", []),
        rotation_signals=scoring_data.get("rotation_signals", []),
        news_impacts=[],
        report=report,
    )

    logger.info("Analyst Agent: analysis complete. Regime=%s", regime_data.get("regime"))
    return {"analysis_results": analysis_results}
