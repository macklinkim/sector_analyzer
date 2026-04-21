"""Crypto Analyst — generates daily AI scores for tracked coins.

Runs once per day with Haiku (single batched prompt) to keep cost minimal.
Input: coin metadata (rank/symbol/name) + recent news headlines grouped by coin.
Output: per-coin ``ai_score`` (-1..+1), ``recommendation`` (overweight/neutral/underweight), ``reasoning``.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

import anthropic

from app.config import Settings

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """당신은 암호화폐 시황 애널리스트입니다. 각 코인에 대해 다음을 산출하세요.

- ai_score: -1.0(강한 매도) ~ +1.0(강한 매수). 최근 뉴스 흐름 + 프로젝트 펀더멘털 + 섹터 내 상대 강도 고려.
- recommendation: overweight / neutral / underweight
- reasoning: 한 문장 한국어 근거. 뉴스 기반이면 어떤 사건인지 언급. 확인되지 않은 정보는 "불확실" 명시.

출력은 반드시 JSON. "scores": [{"coin_id", "ai_score", "recommendation", "reasoning"}] 형태. 다른 텍스트 금지.
본 분석은 AI의 추론이며 실제 투자 판단의 근거로 사용될 수 없음."""


_CATEGORY_LABELS: dict[str, str] = {
    "major": "대형",
    "ai": "AI",
    "defi": "DeFi",
    "l2": "L2",
    "meme": "Meme",
}


def _build_user_prompt(coins: list[dict[str, Any]], news: list[dict[str, Any]]) -> str:
    coin_lines: list[str] = []
    for c in coins:
        category = c.get("category") or ("ai" if c.get("is_ai") else "major")
        label = _CATEGORY_LABELS.get(category, category)
        rank = c.get("market_cap_rank") or "?"
        coin_lines.append(
            f"- [{label}] {c['coin_id']} ({c['symbol'].upper()}) — {c['name']}, 시총순위 {rank}"
        )

    # Group recent news by coin symbol for compact context.
    by_symbol: dict[str, list[dict[str, Any]]] = {}
    for item in news:
        for sym in item.get("related_coins", []) or []:
            by_symbol.setdefault(sym.lower(), []).append(item)

    news_sections: list[str] = []
    for c in coins:
        sym = c["symbol"].lower()
        items = by_symbol.get(sym, [])[:3]  # cap to 3 per coin
        if not items:
            continue
        header = f"## {c['coin_id']} ({sym.upper()}) 관련 뉴스"
        bullets = [
            f"- ({n.get('sentiment', 'neutral')}) {n.get('title', '')}" for n in items
        ]
        news_sections.append(header + "\n" + "\n".join(bullets))

    news_block = "\n\n".join(news_sections) if news_sections else "(최근 관련 뉴스 없음)"

    return (
        "# 추적 대상 코인\n"
        + "\n".join(coin_lines)
        + "\n\n# 최근 24시간 뉴스\n"
        + news_block
        + "\n\n모든 추적 코인에 대해 점수를 산출하세요."
    )


def analyze_crypto_scores(
    coins: list[dict[str, Any]],
    news: list[dict[str, Any]],
    settings: Settings,
) -> list[dict[str, Any]]:
    """Call Claude once for the whole coin list and return parsed score rows."""
    if not coins:
        return []

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    user_prompt = _build_user_prompt(coins, news)

    logger.info("Crypto analyst: %d coins, %d news items", len(coins), len(news))

    resp = client.messages.create(
        model=settings.claude_model_analyst,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = resp.content[0].text if resp.content else ""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json\n"):
            raw = raw[5:]

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error("Crypto analyst JSON parse failed: %s — first 400 chars: %s", e, raw[:400])
        return []

    scores_in = data.get("scores") if isinstance(data, dict) else None
    if not isinstance(scores_in, list):
        logger.error("Crypto analyst response missing 'scores' list: %s", raw[:200])
        return []

    analyzed_at = datetime.now(timezone.utc).isoformat()
    valid_ids = {c["coin_id"] for c in coins}
    out: list[dict[str, Any]] = []
    for row in scores_in:
        coin_id = row.get("coin_id")
        if coin_id not in valid_ids:
            logger.warning("Analyst returned unknown coin_id: %s", coin_id)
            continue
        try:
            score = max(-1.0, min(1.0, float(row.get("ai_score", 0))))
        except (TypeError, ValueError):
            continue
        rec = row.get("recommendation", "neutral")
        if rec not in {"overweight", "neutral", "underweight"}:
            rec = "neutral"
        out.append(
            {
                "coin_id": coin_id,
                "ai_score": score,
                "recommendation": rec,
                "reasoning": (row.get("reasoning") or "").strip()[:500],
                "analyzed_at": analyzed_at,
            }
        )

    return out
