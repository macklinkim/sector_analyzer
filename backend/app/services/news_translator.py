"""Claude Haiku-based batch translator for crypto news headlines.

Takes ~40 English headlines and returns a one-sentence Korean summary per item.
One batched call keeps the daily cost around $0.001.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import anthropic

from app.config import Settings

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = (
    "암호화폐 뉴스 헤드라인을 한글 한 문장으로 핵심만 요약하세요. "
    "원문을 그대로 번역하지 말고 사건/숫자/대상이 드러나도록 압축합니다. "
    "전문 용어는 그대로 유지(BTC, ETH 등). "
    "출력은 반드시 JSON. {\"summaries\":[{\"i\":인덱스,\"ko\":\"한국어 한 문장\"}]} 형식. 다른 텍스트 금지."
)


def translate_headlines(
    news_rows: list[dict[str, Any]],
    settings: Settings,
) -> list[dict[str, Any]]:
    """Return ``news_rows`` with each row's ``title_ko`` populated.

    Falls back to the original English title if translation fails — data is never lost.
    """
    if not news_rows:
        return news_rows

    numbered = "\n".join(f"{i}. {row['title']}" for i, row in enumerate(news_rows))
    user_prompt = f"# 영문 헤드라인 목록\n{numbered}\n\n각 인덱스에 대해 한 문장 한국어 요약."

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        resp = client.messages.create(
            model=settings.claude_model_news,
            max_tokens=4000,  # 40 headlines × Korean summary ~50 tokens + JSON overhead
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = (resp.content[0].text if resp.content else "").strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.lower().startswith("json\n"):
                raw = raw[5:]

        data = json.loads(raw)
        summaries = data.get("summaries") if isinstance(data, dict) else None
        if not isinstance(summaries, list):
            raise ValueError("missing 'summaries' list")

        ko_by_index: dict[int, str] = {}
        for s in summaries:
            idx = s.get("i")
            ko = (s.get("ko") or "").strip()
            if isinstance(idx, int) and 0 <= idx < len(news_rows) and ko:
                ko_by_index[idx] = ko[:300]

    except Exception as e:
        logger.error("News translation failed: %s", e, exc_info=True)
        ko_by_index = {}

    for i, row in enumerate(news_rows):
        row["title_ko"] = ko_by_index.get(i)
    return news_rows
