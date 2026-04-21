"""CoinGecko free public API client — fetches daily coin metadata only.

Live price/volume is streamed to the browser via Binance WebSocket, so we keep
CoinGecko usage to 1-2 calls per day (metadata + AI-category lookup).
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Hand-curated target universe. 'is_ai' flags are authoritative — CoinGecko
# categories are only used as a cross-check for new additions.
TRACKED_COINS: list[dict[str, Any]] = [
    # Large caps
    {"coin_id": "bitcoin", "symbol": "btc", "is_ai": False},
    {"coin_id": "ethereum", "symbol": "eth", "is_ai": False},
    {"coin_id": "solana", "symbol": "sol", "is_ai": False},
    {"coin_id": "binancecoin", "symbol": "bnb", "is_ai": False},
    {"coin_id": "ripple", "symbol": "xrp", "is_ai": False},
    {"coin_id": "cardano", "symbol": "ada", "is_ai": False},
    {"coin_id": "dogecoin", "symbol": "doge", "is_ai": False},
    {"coin_id": "avalanche-2", "symbol": "avax", "is_ai": False},
    {"coin_id": "chainlink", "symbol": "link", "is_ai": False},
    {"coin_id": "polkadot", "symbol": "dot", "is_ai": False},
    {"coin_id": "sui", "symbol": "sui", "is_ai": False},
    {"coin_id": "ondo-finance", "symbol": "ondo", "is_ai": False},
    # AI sector
    {"coin_id": "near", "symbol": "near", "is_ai": True},
    {"coin_id": "render-token", "symbol": "render", "is_ai": True},
    {"coin_id": "fetch-ai", "symbol": "fet", "is_ai": True},
    {"coin_id": "bittensor", "symbol": "tao", "is_ai": True},
]

BASE_URL = "https://api.coingecko.com/api/v3"


async def fetch_coin_metadata() -> list[dict[str, Any]]:
    """Fetch one batch of market data for all TRACKED_COINS.

    Uses the single ``/coins/markets?ids=...`` endpoint — costs 1 API call
    regardless of how many coin IDs we pass.
    """
    ids = ",".join(c["coin_id"] for c in TRACKED_COINS)
    flags = {c["coin_id"]: c["is_ai"] for c in TRACKED_COINS}

    params = {
        "vs_currency": "usd",
        "ids": ids,
        "order": "market_cap_desc",
        "per_page": str(len(TRACKED_COINS)),
        "page": "1",
        "sparkline": "false",
        "price_change_percentage": "24h",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{BASE_URL}/coins/markets", params=params)
        resp.raise_for_status()
        rows: list[dict[str, Any]] = resp.json()

    out: list[dict[str, Any]] = []
    for row in rows:
        coin_id = row.get("id")
        if coin_id not in flags:
            continue
        out.append(
            {
                "coin_id": coin_id,
                "symbol": (row.get("symbol") or "").lower(),
                "name": row.get("name") or coin_id,
                "market_cap": row.get("market_cap"),
                "market_cap_rank": row.get("market_cap_rank"),
                "image_url": row.get("image"),
                "is_ai": flags[coin_id],
            }
        )

    if len(out) < len(TRACKED_COINS):
        missing = set(flags) - {r["coin_id"] for r in out}
        logger.warning("CoinGecko returned fewer coins than requested (missing: %s)", missing)

    return out
