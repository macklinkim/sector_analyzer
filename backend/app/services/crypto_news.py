"""Crypto news via public RSS feeds — no API key required, no rate limit.

CryptoPanic's free tier was discontinued 2026-04-01 and CryptoCompare now
requires an API key even for the news endpoint, so we aggregate RSS directly
from major crypto publications. Related coins are inferred from the headline
by matching configured symbols and name aliases.
"""
from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import feedparser

logger = logging.getLogger(__name__)

FEEDS: list[tuple[str, str]] = [
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("CoinTelegraph", "https://cointelegraph.com/rss"),
    ("Decrypt", "https://decrypt.co/feed"),
    ("The Block", "https://www.theblock.co/rss.xml"),
]

# Symbol → list of aliases to match in titles. Kept small to avoid false positives
# (a bare "LINK" hits everywhere; we require the alias form).
SYMBOL_ALIASES: dict[str, list[str]] = {
    "btc": ["bitcoin", "btc"],
    "eth": ["ethereum", "ether", "eth"],
    "sol": ["solana", "sol"],
    "bnb": ["binance coin", "bnb"],
    "xrp": ["ripple", "xrp"],
    "ada": ["cardano", "ada"],
    "doge": ["dogecoin", "doge"],
    "avax": ["avalanche", "avax"],
    "link": ["chainlink"],
    "dot": ["polkadot", "dot"],
    "sui": ["sui"],
    "ondo": ["ondo"],
    "near": ["near protocol", "near"],
    "render": ["render", "rndr"],
    "fet": ["fetch.ai", "fetch ai", "artificial superintelligence alliance"],
    "tao": ["bittensor", "tao"],
}


def _parse_published(entry: Any) -> datetime | None:
    for attr in ("published", "updated", "created"):
        raw = getattr(entry, attr, None)
        if not raw:
            continue
        try:
            dt = parsedate_to_datetime(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (TypeError, ValueError):
            continue
    parsed = getattr(entry, "published_parsed", None)
    if parsed:
        try:
            return datetime(*parsed[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            return None
    return None


def _match_coins(title: str, tracked: list[str]) -> list[str]:
    """Return tracked symbols whose aliases appear in the title (case-insensitive word match)."""
    lowered = title.lower()
    matched: list[str] = []
    for sym in tracked:
        aliases = SYMBOL_ALIASES.get(sym, [sym])
        for alias in aliases:
            # Word-boundary match so "near" in "nearby" doesn't trigger
            if re.search(rf"\b{re.escape(alias.lower())}\b", lowered):
                matched.append(sym)
                break
    return matched


def _parse_feed_sync(name: str, url: str, tracked: list[str]) -> list[dict[str, Any]]:
    parsed = feedparser.parse(url)
    if parsed.bozo:
        logger.warning("RSS parse issue for %s: %s", name, parsed.bozo_exception)

    rows: list[dict[str, Any]] = []
    for entry in parsed.entries:
        url_ = getattr(entry, "link", None)
        title = getattr(entry, "title", None)
        if not url_ or not title:
            continue

        matched = _match_coins(title, tracked)
        if not matched:
            continue

        published = _parse_published(entry)
        if published is None:
            continue

        rows.append(
            {
                "url": url_,
                "title": title,
                "source": name,
                "published_at": published.isoformat(),
                "sentiment": "neutral",
                "related_coins": matched,
            }
        )
    return rows


async def fetch_crypto_news(
    coin_symbols: list[str],
    limit: int = 40,
) -> list[dict[str, Any]]:
    """Pull RSS from all FEEDS in parallel, filter to tracked coins, dedupe by URL."""
    tracked = [s.lower() for s in coin_symbols]

    loop = asyncio.get_running_loop()
    tasks = [
        loop.run_in_executor(None, _parse_feed_sync, name, url, tracked)
        for name, url in FEEDS
    ]
    per_feed = await asyncio.gather(*tasks, return_exceptions=True)

    seen: set[str] = set()
    merged: list[dict[str, Any]] = []
    for result in per_feed:
        if isinstance(result, Exception):
            logger.warning("Feed task failed: %s", result)
            continue
        for row in result:
            if row["url"] in seen:
                continue
            seen.add(row["url"])
            merged.append(row)

    merged.sort(key=lambda r: r["published_at"], reverse=True)
    logger.info("RSS crypto news: %d articles (from %d feeds)", len(merged), len(FEEDS))
    return merged[:limit]
