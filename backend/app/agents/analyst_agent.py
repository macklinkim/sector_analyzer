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
    """Classify macro environment from US10Y, DXY, WTI, Gold directions and values."""
    dirs: dict[str, str] = {}
    values: dict[str, dict] = {}
    for ind in indicators:
        name = ind.get("indicator_name", "")
        dirs[name] = ind.get("change_direction", "flat")
        values[name] = {
            "value": ind.get("value"),
            "change_percent": ind.get("change_percent"),
            "change_direction": ind.get("change_direction", "flat"),
        }

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
        "indicator_values": values,
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
# Step 2.5: Cross-Validation — sentiment vs momentum divergence (rule-based)
# ---------------------------------------------------------------------------

def cross_validate_candidates(
    candidates: list[dict],
    news_sentiment: dict[str, float],
) -> list[dict]:
    """Detect sentiment-momentum divergence and adjust candidates.

    | Sentiment | Momentum | Action                                       |
    |-----------|----------|----------------------------------------------|
    | positive  | up       | keep as-is                                   |
    | positive  | down     | suppress signal (Divergence warning)         |
    | negative  | up       | keep, confidence -0.1 (Contrarian)           |
    | negative  | down     | keep as rotate_out candidate                 |
    """
    validated: list[dict] = []
    for c in candidates:
        sym = c["symbol"]
        sentiment = news_sentiment.get(sym, 0.0)
        m1w = c.get("momentum", {}).get("momentum_1w", 0)

        sentiment_positive = sentiment > 0
        momentum_up = m1w > 0

        if sentiment_positive and not momentum_up:
            # Divergence — suppress
            c["flags"].append("센티먼트-가격괴리(억제)")
            c["score"] = round(c["score"] * 0.5, 3)
            c["cross_validation"] = "divergence_suppressed"
        elif not sentiment_positive and momentum_up:
            # Contrarian — keep but penalize confidence
            c["flags"].append("역발상(confidence감점)")
            c["cross_validation"] = "contrarian"
        else:
            c["cross_validation"] = "aligned"

        validated.append(c)

    validated.sort(key=lambda x: x["score"], reverse=True)
    return validated


def extract_news_sentiment(news_data: object) -> dict[str, float]:
    """Extract per-sector sentiment from news data.

    Simple heuristic: count positive/negative keywords in article titles
    mentioning sector-related terms.
    """
    sector_keywords: dict[str, list[str]] = {
        "XLK": ["tech", "technology", "ai", "semiconductor", "chip", "software"],
        "XLF": ["bank", "financial", "fed", "interest rate", "lending"],
        "XLE": ["oil", "energy", "crude", "opec", "gas", "drilling"],
        "XLV": ["health", "pharma", "biotech", "drug", "fda", "medical"],
        "XLI": ["industrial", "manufacturing", "infrastructure", "defense"],
        "XLY": ["consumer", "retail", "amazon", "tesla", "spending"],
        "XLP": ["staple", "grocery", "food", "beverage", "household"],
        "XLU": ["utility", "utilities", "electric", "power", "grid"],
        "XLB": ["material", "mining", "chemical", "steel", "commodity"],
        "XLRE": ["real estate", "reit", "housing", "mortgage", "property"],
        "XLC": ["communication", "media", "google", "meta", "streaming"],
    }
    positive_words = {"surge", "rally", "gain", "rise", "jump", "boost", "strong", "bullish", "up", "growth", "beat"}
    negative_words = {"fall", "drop", "decline", "crash", "slump", "weak", "bearish", "down", "loss", "miss", "cut"}

    sentiment: dict[str, float] = {}
    if not news_data:
        return sentiment

    all_articles: list[dict] = []
    for articles in news_data.articles_by_category.values():
        all_articles.extend(articles)

    for sym, keywords in sector_keywords.items():
        pos_count = 0
        neg_count = 0
        for article in all_articles:
            title = ((article.get("title") or "") + " " + (article.get("description") or "")).lower()
            if not any(kw in title for kw in keywords):
                continue
            pos_count += sum(1 for w in positive_words if w in title)
            neg_count += sum(1 for w in negative_words if w in title)

        total = pos_count + neg_count
        if total > 0:
            sentiment[sym] = round((pos_count - neg_count) / total, 2)
        else:
            sentiment[sym] = 0.0

    return sentiment


# ---------------------------------------------------------------------------
# Step 3: Claude AI final analysis with full context
# ---------------------------------------------------------------------------

ANALYST_SYSTEM_PROMPT = """미국 주식 섹터 로테이션 분석가로서 **3단계 검증** 후 시그널을 생성하세요.

## Regime 판정
- Goldilocks: 성장↑ 물가↓ (Risk-On)
- Reflation: 성장↑ 물가↑ (Overheating)
- Stagflation: 성장↓ 물가↑ (Worst)
- Deflation: 성장↓ 물가↓ (Safe Haven)

## 시그널 등급
- [MAJOR] Regime Shift: 매크로 변화 + RS>2% 골든크로스 + 거래량↑. 섹터당 월 1~2회 미만, 확신도 ≥0.7.
- [ALERT] Momentum Surge: 뉴스 촉매 + 1W 모멘텀 급증 + RS>0. 확신도 0.5~0.7.
- [WATCH] RS Improving: RS (-)→(+), S&P500 대비 덜 하락. 확신도 0.3~0.5.

## 제약 규칙
- rotate_in엔 대응 rotate_out 섹터 필수 명시. 3개 이상 rotate_in이면 상위 2개만.
- regime_shift는 배치당 최대 1건.
- 매크로 지표(금리/달러/유가/금)의 **수치·변화폭** 반드시 근거로 인용. 뉴스 센티먼트 단독 판단 금지.
- cross_validation="divergence_suppressed"면 시그널 금지. "contrarian"이면 confidence -0.1.
- 매크로-RS 불일치(예: 금리↑시 Tech RS↑)는 Fake Signal로 제외.
- 모든 섹터 동시 Regime Shift 금지. 최대 2~3개 시그널.
- 사전필터 score<0.3 후보는 제외.

## 응답 형식 (JSON만, 다른 텍스트 없이):
{
  "regime": {
    "regime": "goldilocks|reflation|stagflation|deflation",
    "growth_direction": "high|low",
    "inflation_direction": "high|low",
    "regime_probabilities": {"goldilocks": 0.0, "reflation": 0.0, "stagflation": 0.0, "deflation": 0.0},
    "reasoning": "한글 설명"
  },
  "scoreboards": [{
    "sector_name": "...", "etf_symbol": "...",
    "base_score": 0.0, "override_score": 0.0,
    "news_sentiment_score": 0.0, "momentum_score": 0.0,
    "final_score": 0.0, "rank": 1,
    "recommendation": "overweight|neutral|underweight",
    "reasoning": "한글 설명"
  }],
  "rotation_signals": [{
    "signal_type": "rotate_in|rotate_out|regime_shift",
    "signal_grade": "MAJOR|ALERT|WATCH",
    "from_sector": null, "to_sector": "...",
    "strength": 0.0, "final_score": 0.0,
    "confidence_score": 0.0,
    "macro_environment": "...",
    "reasoning": "한글 설명 (매크로→RS→모멘텀 3단계 근거)"
  }],
  "report_summary": "한글 종합 요약",
  "key_highlights": ["포인트1", "포인트2", "포인트3"]
}"""


def _build_analyst_user_content(
    macro_env_json: str,
    candidates_json: str,
    momentum_detail: str,
    news_summary: str,
    sector_mapping_json: str,
    environment: str,
) -> str:
    """Dynamic context sent on every call — not cache-eligible."""
    return f"""## 매크로 환경 (현재: {environment})
{macro_env_json}

## 시그널 후보 (사전필터 통과, cross_validation 포함)
{candidates_json}

## 섹터별 모멘텀+RS
{momentum_detail}

## 뉴스 요약
{news_summary}

## 섹터-국면 매핑 (Override 규칙 포함)
{sector_mapping_json}"""


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
    top_candidates = [c for c in candidates if c["score"] >= 0.4]
    logger.info("Step 2 — %d/%d candidates passed pre-filter", len(top_candidates), len(candidates))

    # ---- Step 2.5: Cross-Validation (sentiment vs momentum) ----
    news_sentiment = extract_news_sentiment(news_data)
    top_candidates = cross_validate_candidates(top_candidates, news_sentiment)
    logger.info("Step 2.5 — Cross-validation applied, sentiment map: %s", news_sentiment)

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

    user_content = _build_analyst_user_content(
        macro_env_json=json.dumps(macro_env, default=str, ensure_ascii=False),
        candidates_json=json.dumps(top_candidates, default=str, ensure_ascii=False),
        momentum_detail=momentum_detail,
        news_summary=news_summary,
        sector_mapping_json=json.dumps(sector_mapping, default=str, ensure_ascii=False),
        environment=macro_env["environment"],
    )

    logger.info(
        "Analyst AI prompt preview (model=%s, user_chars=%d): %s",
        settings.claude_model_analyst, len(user_content), user_content[:600],
    )

    try:
        response = client.messages.create(
            model=settings.claude_model_analyst,
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": ANALYST_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                },
            ],
            messages=[{"role": "user", "content": user_content}],
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

    # ---- Post-process signals: enforce limits (v2) ----
    signals = result.get("rotation_signals", [])
    # Filter: remove low-confidence
    signals = [s for s in signals if float(s.get("confidence_score", 0)) >= 0.3]
    # regime_shift는 confidence >= 0.7만 허용
    signals = [
        s for s in signals
        if s.get("signal_type") != "regime_shift" or float(s.get("confidence_score", 0)) >= 0.7
    ]
    # 최대 3개로 제한
    signals = signals[:3]
    # regime_shift는 배치당 1건만
    regime_shifts = [s for s in signals if s.get("signal_type") == "regime_shift"]
    if len(regime_shifts) > 1:
        signals = [s for s in signals if s.get("signal_type") != "regime_shift"]
        signals.insert(0, regime_shifts[0])
        signals = signals[:3]
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
