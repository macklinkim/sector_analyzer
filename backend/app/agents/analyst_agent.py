# backend/app/agents/analyst_agent.py
"""Analyst Agent — 3-Step Validation for Rotation Signals.

Step 1: Macro Environment Check (Economic Indicators → Risk-On/Off/Inflationary/Deflationary)
Step 2: RS & Momentum Cross (Golden Cross, momentum alignment)
Step 3: Sparkline Trend Confirmation (via Claude AI with full context)
"""
import json
import logging
from datetime import datetime, timezone

import anthropic
from langchain_core.runnables import RunnableConfig

from app.agents.state import MarketAnalysisState, AnalysisResults
from app.config import Settings
from app.services.supabase import SupabaseService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Step 1: Macro Environment — rule-based from economic indicators
# ---------------------------------------------------------------------------

def classify_macro_environment(indicators: list[dict]) -> dict:
    """Classify macro environment from US10Y, DXY, WTI, Gold directions."""
    dirs: dict[str, str] = {}
    for ind in indicators:
        dirs[ind.get("indicator_name", "")] = ind.get("change_direction", "flat")

    us10y = dirs.get("US 10Y Treasury", "flat")
    dxy = dirs.get("DXY Dollar Index", "flat")
    wti = dirs.get("WTI Crude Oil", "flat")
    gold = dirs.get("Gold", "flat")

    # Classification logic
    risk_on_score = 0
    inflation_score = 0

    # Gold up + Oil down = deflationary fear, risk-off
    if gold == "up":
        risk_on_score -= 1
        inflation_score -= 1
    if gold == "down":
        risk_on_score += 1

    # Rate down = dovish, growth concern but good for equities
    if us10y == "down":
        risk_on_score += 0.5
        inflation_score -= 1
    if us10y == "up":
        inflation_score += 1
        risk_on_score -= 0.5

    # Dollar down = risk-on, liquidity
    if dxy == "down":
        risk_on_score += 1
    if dxy == "up":
        risk_on_score -= 0.5

    # Oil up = inflationary
    if wti == "up":
        inflation_score += 1
    if wti == "down":
        inflation_score -= 1

    if risk_on_score > 0 and inflation_score <= 0:
        env = "Risk-On"
    elif risk_on_score <= 0 and inflation_score <= 0:
        env = "Deflationary"
    elif risk_on_score > 0 and inflation_score > 0:
        env = "Inflationary"
    else:
        env = "Risk-Off"

    # Sector implications
    sector_bias: dict[str, float] = {}
    if env == "Risk-On":
        sector_bias = {"XLK": 0.3, "XLY": 0.2, "XLC": 0.2, "XLF": 0.1}
    elif env == "Deflationary":
        sector_bias = {"XLU": 0.3, "XLV": 0.2, "XLP": 0.2, "XLRE": 0.1}
    elif env == "Inflationary":
        sector_bias = {"XLE": 0.3, "XLB": 0.2, "XLI": 0.1}
    else:  # Risk-Off
        sector_bias = {"XLU": 0.2, "XLV": 0.2, "XLP": 0.2, "XLE": 0.1}

    return {
        "environment": env,
        "risk_on_score": risk_on_score,
        "inflation_score": inflation_score,
        "indicator_dirs": dirs,
        "sector_bias": sector_bias,
    }


# ---------------------------------------------------------------------------
# Step 2: RS & Momentum pre-filter — rule-based
# ---------------------------------------------------------------------------

def compute_signal_candidates(
    sectors: list[dict],
    momentum: dict[str, dict],
    relative_strength: dict[str, float],
    macro_env: dict,
) -> list[dict]:
    """Pre-filter sectors that pass RS and momentum thresholds."""
    candidates = []
    sector_bias = macro_env.get("sector_bias", {})

    for sec in sectors:
        sym = sec.get("symbol", sec.get("etf_symbol", ""))
        rs = relative_strength.get(sym, 0.0)
        mom = momentum.get(sym, {})
        m1w = mom.get("momentum_1w", 0)
        m1m = mom.get("momentum_1m", 0)
        m3m = mom.get("momentum_3m", 0)
        m1y = mom.get("momentum_1y", 0)

        # RS filter: strong (>2%) or golden cross (1m negative but improving)
        rs_strong = rs > 2.0
        rs_golden_cross = rs > 0 and m1m < 0  # RS positive but 1M return still negative = turning point

        # Momentum alignment: all positive or short-term recovery
        all_positive = m1w > 0 and m1m > 0 and m3m > 0
        short_term_recovery = m1w > 0 and m1w > m1m  # 1W recovering faster than 1M

        # Macro alignment bonus
        macro_bonus = sector_bias.get(sym, 0.0)
        macro_aligned = macro_bonus > 0

        # Compute raw score
        score = 0.0
        flags: list[str] = []

        if rs_strong:
            score += 0.3
            flags.append(f"RS강세({rs:+.1f}%)")
        if rs_golden_cross:
            score += 0.2
            flags.append("RS골든크로스")
        if all_positive:
            score += 0.2
            flags.append("모멘텀정렬")
        if short_term_recovery:
            score += 0.15
            flags.append("단기회복세")
        if macro_aligned:
            score += macro_bonus
            flags.append(f"매크로일치({macro_env['environment']})")

        # Anti-signal: macro misalignment penalty
        if not macro_aligned and rs_strong:
            score -= 0.15
            flags.append("매크로불일치주의")

        candidates.append({
            "symbol": sym,
            "name": sec.get("name", sym),
            "rs": rs,
            "momentum": mom,
            "score": round(score, 3),
            "flags": flags,
            "macro_bonus": macro_bonus,
        })

    # Sort by score descending
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates


# ---------------------------------------------------------------------------
# Step 3: Claude AI final analysis with full context
# ---------------------------------------------------------------------------

ANALYSIS_PROMPT = """당신은 미국 주식 섹터 로테이션 전문 분석가입니다. 아래 데이터를 기반으로 **엄격한 3단계 검증**을 거쳐 시그널을 생성하세요.

## 현재 매크로 환경
{macro_env_json}

## 시그널 후보 (사전 필터링 결과)
{candidates_json}

## 섹터별 모멘텀 & RS 상세
{momentum_detail}

## 뉴스 요약
{news_summary}

## 섹터-국면 매핑 (Override 규칙 포함)
{sector_mapping}

---

## 분석 지침

### 국면(Regime) 판정
매크로 환경({environment})을 고려하여 현재 Macro Regime을 판정하세요.
- Goldilocks: 성장↑ + 물가↓ — Risk-On
- Reflation: 성장↑ + 물가↑ — Overheating
- Stagflation: 성장↓ + 물가↑ — Worst
- Deflation: 성장↓ + 물가↓ — Safe Haven

### 시그널 등급 (엄격히 제한)
1. **[MAJOR]** Regime Shift (강력 전환):
   - 조건: 매크로 환경 변화 + RS > 2% 골든크로스 + 거래량 동반 상승
   - 빈도: 한 달에 섹터당 1~2회 미만. 확신도 0.7 이상만.

2. **[ALERT]** Momentum Surge (수급 포착):
   - 조건: 뉴스 촉매 + 1W 모멘텀 급증 + RS 양수
   - 확신도 0.5~0.7

3. **[WATCH]** RS Improving (개선 중):
   - 조건: RS 마이너스→플러스 전환 중, S&P500 대비 덜 하락
   - 확신도 0.3~0.5

### Fake Signal 필터링
- 매크로 환경과 RS가 불일치하면 (예: 금리 상승기에 기술주 RS 상승) → Fake Signal로 제외
- 모든 섹터에 동시 Regime Shift → 잘못된 분석. 최대 2~3개 시그널만.
- 사전 필터 score가 0.3 미만인 후보는 시그널 생성 금지.

---

## 응답 형식 (JSON만, 다른 텍스트 없이):
{{
  "regime": {{
    "regime": "goldilocks|reflation|stagflation|deflation",
    "growth_direction": "high|low",
    "inflation_direction": "high|low",
    "regime_probabilities": {{"goldilocks": 0.0, "reflation": 0.0, "stagflation": 0.0, "deflation": 0.0}},
    "reasoning": "한글 설명"
  }},
  "scoreboards": [
    {{
      "sector_name": "...", "etf_symbol": "...",
      "base_score": 0.0, "override_score": 0.0,
      "news_sentiment_score": 0.0, "momentum_score": 0.0,
      "final_score": 0.0, "rank": 1,
      "recommendation": "overweight|neutral|underweight",
      "reasoning": "한글 설명"
    }}
  ],
  "rotation_signals": [
    {{
      "signal_type": "rotate_in|rotate_out|regime_shift",
      "signal_grade": "MAJOR|ALERT|WATCH",
      "from_sector": null, "to_sector": "...",
      "strength": 0.0, "final_score": 0.0,
      "confidence_score": 0.0,
      "macro_environment": "{environment}",
      "reasoning": "한글 설명 (매크로→RS→모멘텀 3단계 근거)"
    }}
  ],
  "report_summary": "한글 종합 요약",
  "key_highlights": ["포인트1", "포인트2", "포인트3"]
}}"""


async def analyst_agent_node(state: MarketAnalysisState, config: RunnableConfig) -> dict:
    """LangGraph node: 3-Step Validation for sector rotation signals."""
    logger.info("Analyst Agent: starting 3-step analysis (batch=%s)", state["batch_type"])

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

    # ---- Step 1: Macro Environment Classification ----
    indicators = market_data.economic_indicators if market_data else []
    macro_env = classify_macro_environment(indicators)
    logger.info("Step 1 — Macro Environment: %s (risk=%.1f, inflation=%.1f)",
                macro_env["environment"], macro_env["risk_on_score"], macro_env["inflation_score"])

    # ---- Step 2: RS & Momentum Pre-filter ----
    sectors = market_data.sectors if market_data else []
    momentum = market_data.momentum if market_data else {}
    rs = market_data.relative_strength if market_data else {}
    candidates = compute_signal_candidates(sectors, momentum, rs, macro_env)
    top_candidates = [c for c in candidates if c["score"] >= 0.2]
    logger.info("Step 2 — %d/%d candidates passed pre-filter", len(top_candidates), len(candidates))

    # ---- Step 3: Claude AI final analysis ----
    news_summary = ""
    if news_data:
        for cat, articles in news_data.articles_by_category.items():
            news_summary += f"\n### {cat}\n"
            for a in articles[:3]:
                news_summary += f"- {a.get('title', '')}: {a.get('description', '')}\n"

    momentum_detail = json.dumps({
        sym: {"momentum": momentum.get(sym, {}), "rs": rs.get(sym, 0.0)}
        for sec in sectors
        for sym in [sec.get("symbol", sec.get("etf_symbol", ""))]
    }, default=str, ensure_ascii=False)

    prompt = ANALYSIS_PROMPT.format(
        macro_env_json=json.dumps(macro_env, default=str, ensure_ascii=False),
        candidates_json=json.dumps(top_candidates, default=str, ensure_ascii=False),
        momentum_detail=momentum_detail,
        news_summary=news_summary,
        sector_mapping=json.dumps(sector_mapping, default=str, ensure_ascii=False),
        environment=macro_env["environment"],
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        # Extract JSON
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            result = json.loads(raw[start:end])
        else:
            raise ValueError("No JSON object found in response")
    except Exception as e:
        logger.error("Claude analysis failed: %s", e)
        result = {
            "regime": {
                "regime": "goldilocks", "growth_direction": "high", "inflation_direction": "low",
                "regime_probabilities": {"goldilocks": 0.25, "reflation": 0.25, "stagflation": 0.25, "deflation": 0.25},
                "reasoning": "분석 실패 — 기본값 사용",
            },
            "scoreboards": [],
            "rotation_signals": [],
            "report_summary": "분석 실패",
            "key_highlights": [],
        }

    # ---- Post-process regime ----
    regime_data = result.get("regime", {})
    regime_data["batch_type"] = batch_type
    regime_data["analyzed_at"] = now.isoformat()

    # ---- Post-process scoreboards ----
    for sb in result.get("scoreboards", []):
        sb["batch_type"] = batch_type
        sb["scored_at"] = now.isoformat()

    # ---- Post-process signals: enforce limits ----
    signals = result.get("rotation_signals", [])
    # Filter: max 5 signals, remove low-confidence
    signals = [s for s in signals if float(s.get("confidence_score", 0)) >= 0.3]
    signals = signals[:5]
    for sig in signals:
        sig["batch_type"] = batch_type
        sig["detected_at"] = now.isoformat()
        sig["macro_environment"] = macro_env["environment"]
        # Ensure signal_grade exists
        if "signal_grade" not in sig:
            conf = float(sig.get("confidence_score", 0.5))
            if conf >= 0.7:
                sig["signal_grade"] = "MAJOR"
            elif conf >= 0.5:
                sig["signal_grade"] = "ALERT"
            else:
                sig["signal_grade"] = "WATCH"

    logger.info("Step 3 — %d signals generated (env=%s, regime=%s)",
                len(signals), macro_env["environment"], regime_data.get("regime"))

    report = {
        "batch_type": batch_type,
        "summary": result.get("report_summary", ""),
        "key_highlights": result.get("key_highlights", []),
        "report_date": now.strftime("%Y-%m-%d"),
        "analyzed_at": now.isoformat(),
        "disclaimer": "본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다.",
    }

    analysis_results = AnalysisResults(
        regime=regime_data,
        scoreboards=result.get("scoreboards", []),
        rotation_signals=signals,
        news_impacts=[],
        report=report,
    )

    return {"analysis_results": analysis_results}
