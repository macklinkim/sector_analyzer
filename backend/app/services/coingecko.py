"""CoinGecko free public API client — fetches daily coin metadata only.

Live price/volume is streamed to the browser via Binance WebSocket, so we keep
CoinGecko usage to 1-2 calls per day (metadata + AI-category lookup).
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Hand-curated target universe grouped by category. The category column drives
# the frontend sector filter; is_ai is kept as a derived convenience (category == 'ai').
TRACKED_COINS: list[dict[str, Any]] = [
    # Large caps
    {"coin_id": "bitcoin", "symbol": "btc", "category": "major"},
    {"coin_id": "ethereum", "symbol": "eth", "category": "major"},
    {"coin_id": "solana", "symbol": "sol", "category": "major"},
    {"coin_id": "binancecoin", "symbol": "bnb", "category": "major"},
    {"coin_id": "ripple", "symbol": "xrp", "category": "major"},
    {"coin_id": "cardano", "symbol": "ada", "category": "major"},
    {"coin_id": "dogecoin", "symbol": "doge", "category": "major"},
    {"coin_id": "avalanche-2", "symbol": "avax", "category": "major"},
    {"coin_id": "chainlink", "symbol": "link", "category": "major"},
    {"coin_id": "polkadot", "symbol": "dot", "category": "major"},
    {"coin_id": "sui", "symbol": "sui", "category": "major"},
    {"coin_id": "ondo-finance", "symbol": "ondo", "category": "major"},
    # AI sector
    {"coin_id": "near", "symbol": "near", "category": "ai"},
    {"coin_id": "render-token", "symbol": "render", "category": "ai"},
    {"coin_id": "fetch-ai", "symbol": "fet", "category": "ai"},
    {"coin_id": "bittensor", "symbol": "tao", "category": "ai"},
    # DeFi
    {"coin_id": "uniswap", "symbol": "uni", "category": "defi"},
    {"coin_id": "aave", "symbol": "aave", "category": "defi"},
    {"coin_id": "maker", "symbol": "mkr", "category": "defi"},
    # L2 Scaling
    {"coin_id": "arbitrum", "symbol": "arb", "category": "l2"},
    {"coin_id": "optimism", "symbol": "op", "category": "l2"},
    {"coin_id": "matic-network", "symbol": "pol", "category": "l2"},
    # Meme
    {"coin_id": "dogwifcoin", "symbol": "wif", "category": "meme"},
    {"coin_id": "pepe", "symbol": "pepe", "category": "meme"},
    {"coin_id": "bonk", "symbol": "bonk", "category": "meme"},
]

BASE_URL = "https://api.coingecko.com/api/v3"


async def fetch_coin_metadata() -> list[dict[str, Any]]:
    """Fetch one batch of market data for all TRACKED_COINS.

    Uses the single ``/coins/markets?ids=...`` endpoint — costs 1 API call
    regardless of how many coin IDs we pass.
    """
    ids = ",".join(c["coin_id"] for c in TRACKED_COINS)
    categories = {c["coin_id"]: c["category"] for c in TRACKED_COINS}

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
        if coin_id not in categories:
            continue
        category = categories[coin_id]
        out.append(
            {
                "coin_id": coin_id,
                "symbol": (row.get("symbol") or "").lower(),
                "name": row.get("name") or coin_id,
                "market_cap": row.get("market_cap"),
                "market_cap_rank": row.get("market_cap_rank"),
                "image_url": row.get("image"),
                "is_ai": category == "ai",
                "category": category,
            }
        )

    if len(out) < len(TRACKED_COINS):
        missing = set(categories) - {r["coin_id"] for r in out}
        logger.warning("CoinGecko returned fewer coins than requested (missing: %s)", missing)

    return out
