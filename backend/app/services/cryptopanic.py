"""CryptoPanic free API client — daily crypto news fetch.

Free tier (Developer API): ~200 req/day. We call once per day batch so quota is a non-issue.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://cryptopanic.com/api/v1"


def _normalize_votes(votes: dict[str, Any] | None) -> str:
    """Collapse CryptoPanic's vote counts into a single sentiment label."""
    if not votes:
        return "neutral"
    positive = int(votes.get("positive") or 0) + int(votes.get("liked") or 0)
    negative = int(votes.get("negative") or 0) + int(votes.get("disliked") or 0)
    if positive > negative * 1.5:
        return "positive"
    if negative > positive * 1.5:
        return "negative"
    return "neutral"


async def fetch_crypto_news(
    api_key: str,
    coin_symbols: list[str],
    limit: int = 40,
) -> list[dict[str, Any]]:
    """Return recent posts mentioning any of ``coin_symbols``.

    CryptoPanic's ``currencies`` filter accepts comma-separated uppercase tickers.
    ``limit`` is a soft cap — the free tier returns 20 per page, so we may page once.
    """
    if not api_key:
        logger.warning("CRYPTOPANIC_API_KEY not set — returning empty news list")
        return []

    currencies = ",".join(s.upper() for s in coin_symbols)
    params = {
        "auth_token": api_key,
        "currencies": currencies,
        "public": "true",
        "kind": "news",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{BASE_URL}/posts/", params=params)
        resp.raise_for_status()
        payload: dict[str, Any] = resp.json()

    out: list[dict[str, Any]] = []
    for row in payload.get("results", [])[:limit]:
        url = row.get("url")
        title = row.get("title")
        if not url or not title:
            continue

        published_raw = row.get("published_at")
        try:
            published_at = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
        except (AttributeError, ValueError):
            logger.debug("CryptoPanic row missing valid published_at: %s", published_raw)
            continue

        currencies_list = row.get("currencies") or []
        related = [c.get("code", "").lower() for c in currencies_list if c.get("code")]

        out.append(
            {
                "url": url,
                "title": title,
                "source": (row.get("source") or {}).get("title"),
                "published_at": published_at.isoformat(),
                "sentiment": _normalize_votes(row.get("votes")),
                "related_coins": related,  # symbols — caller can map to coin_ids
            }
        )

    return out
