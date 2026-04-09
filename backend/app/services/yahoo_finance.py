"""Yahoo Finance data service — free replacement for EODHD."""
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import yfinance as yf

logger = logging.getLogger(__name__)

SECTOR_ETFS = [
    ("Financials", "XLF"),
    ("Real Estate", "XLRE"),
    ("Technology", "XLK"),
    ("Communication Services", "XLC"),
    ("Consumer Discretionary", "XLY"),
    ("Industrials", "XLI"),
    ("Materials", "XLB"),
    ("Energy", "XLE"),
    ("Utilities", "XLU"),
    ("Healthcare", "XLV"),
    ("Consumer Staples", "XLP"),
]

INDEX_SYMBOLS = [
    ("S&P 500", "^GSPC", "SPY"),
    ("NASDAQ", "^IXIC", "QQQ"),
    ("DOW", "^DJI", "DIA"),
]

MACRO_INDICATORS = [
    ("US 10Y Treasury", "^TNX"),
    ("DXY Dollar Index", "DX-Y.NYB"),
    ("WTI Crude Oil", "CL=F"),
    ("Gold", "GC=F"),
]

_executor = ThreadPoolExecutor(max_workers=4)


def _download_quotes(symbols: list[str], period: str = "5d") -> dict[str, dict]:
    """Synchronous bulk download via yfinance. Returns {symbol: quote_dict}."""
    results: dict[str, dict] = {}
    try:
        data = yf.download(symbols, period=period, progress=False, threads=True)
        if data.empty:
            return results
        for sym in symbols:
            try:
                if len(symbols) == 1:
                    hist = data
                else:
                    hist = data.xs(sym, level="Ticker", axis=1) if "Ticker" in data.columns.names else data[sym]
                if hist.empty or len(hist) < 1:
                    continue
                latest = hist.iloc[-1]
                prev = hist.iloc[-2] if len(hist) > 1 else None
                cur_close = float(latest["Close"])
                prev_close = float(prev["Close"]) if prev is not None else 0.0
                change_p = 0.0
                if prev_close and cur_close:
                    change_p = round((cur_close - prev_close) / prev_close * 100, 2)
                vol = latest.get("Volume", 0)
                vol = int(vol) if vol == vol else 0  # NaN check
                results[sym] = {
                    "close": round(cur_close, 2),
                    "previous_close": round(prev_close, 2),
                    "change_p": change_p,
                    "volume": vol,
                    "date": str(latest.name.date()) if hasattr(latest.name, "date") else "",
                }
            except Exception as e:
                logger.warning("Failed to parse quote for %s: %s", sym, e)
    except Exception as e:
        logger.error("yfinance download failed for %s: %s", symbols, e)
    return results


def _fetch_short_names(symbols: list[str]) -> dict[str, str]:
    """Fetch short company names via yfinance Tickers."""
    names: dict[str, str] = {}
    try:
        tickers = yf.Tickers(" ".join(symbols))
        for sym in symbols:
            try:
                info = tickers.tickers[sym].info
                names[sym] = info.get("shortName") or info.get("longName") or sym
            except Exception:
                names[sym] = sym
    except Exception as e:
        logger.warning("Failed to fetch short names: %s", e)
    return names


def _download_history(symbol: str, period: str = "1mo") -> list[dict]:
    """Synchronous history download for a single symbol."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        if hist.empty:
            return []
        points = []
        for idx, row in hist.iterrows():
            points.append({
                "date": str(idx.date()),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]) if "Volume" in row.index else 0,
            })
        return points
    except Exception as e:
        logger.warning("Failed to fetch history for %s: %s", symbol, e)
        return []


def _fetch_single_quote(symbol: str) -> dict | None:
    """Fetch a single symbol quote via yf.Ticker (works for special symbols like ^TNX, CL=F)."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        if hist.empty or len(hist) < 1:
            return None
        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else None
        cur_close = float(latest["Close"])
        prev_close = float(prev["Close"]) if prev is not None else 0.0
        change_p = 0.0
        if prev_close and cur_close:
            change_p = round((cur_close - prev_close) / prev_close * 100, 2)
        vol = latest.get("Volume", 0)
        vol = int(vol) if vol == vol else 0  # NaN check
        return {
            "close": round(cur_close, 2),
            "previous_close": round(prev_close, 2),
            "change_p": change_p,
            "volume": vol,
        }
    except Exception as e:
        logger.warning("_fetch_single_quote failed for %s: %s", symbol, e)
        return None


class YahooFinanceService:
    """Async wrapper around yfinance (sync lib)."""

    async def _run(self, fn, *args):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, fn, *args)

    # --- Pipeline methods (matching EODHD interface) ---

    async def fetch_indices(self) -> list[dict]:
        yf_symbols = [sym for _, sym, _ in INDEX_SYMBOLS]
        quotes = await self._run(_download_quotes, yf_symbols)
        results = []
        for name, yf_sym, display_sym in INDEX_SYMBOLS:
            q = quotes.get(yf_sym)
            if q:
                results.append({
                    "symbol": display_sym,
                    "name": name,
                    "close": q["close"],
                    "change_p": q["change_p"],
                })
        return results

    async def fetch_sector_etfs(self) -> list[dict]:
        symbols = [sym for _, sym in SECTOR_ETFS]
        quotes = await self._run(_download_quotes, symbols)
        results = []
        for name, symbol in SECTOR_ETFS:
            q = quotes.get(symbol, {})
            results.append({
                "symbol": symbol,
                "name": name,
                "close": q.get("close", 0),
                "change_p": q.get("change_p", 0),
                "volume": q.get("volume", 0),
            })
        return results

    async def fetch_economic_indicators(self) -> list[dict]:
        results = []
        for name, yf_sym in MACRO_INDICATORS:
            try:
                q = await self._run(_fetch_single_quote, yf_sym)
                if not q:
                    logger.warning("No data for indicator %s (%s)", name, yf_sym)
                    continue
                cur = q["close"]
                prev = q["previous_close"]
                if prev and cur:
                    direction = "up" if cur > prev else ("down" if cur < prev else "flat")
                else:
                    direction = "flat"
                results.append({
                    "indicator_name": name,
                    "value": cur,
                    "previous_value": prev,
                    "change_direction": direction,
                    "source": "Yahoo Finance",
                })
            except Exception as e:
                logger.warning("Failed to fetch indicator %s (%s): %s", name, yf_sym, e)
        return results

    async def calculate_momentum(self, symbol: str) -> dict:
        history = await self._run(_download_history, symbol, "1y")
        if not history:
            return {"momentum_1w": 0, "momentum_1m": 0, "momentum_3m": 0, "momentum_6m": 0, "momentum_1y": 0}
        history.reverse()  # newest first
        current = history[0]["close"]

        def pct(idx: int) -> float:
            if idx < len(history) and history[idx]["close"]:
                return round((current - history[idx]["close"]) / history[idx]["close"] * 100, 2)
            return 0.0

        return {
            "momentum_1w": pct(min(5, len(history) - 1)),
            "momentum_1m": pct(min(22, len(history) - 1)),
            "momentum_3m": pct(min(66, len(history) - 1)),
            "momentum_6m": pct(min(132, len(history) - 1)),
            "momentum_1y": pct(min(252, len(history) - 1)),
        }

    async def calculate_52week_range(self, symbol: str) -> dict:
        history = await self._run(_download_history, symbol, "1y")
        if not history:
            return {"week_52_low": 0, "week_52_high": 0}
        prices = [d["close"] for d in history if d.get("close")]
        if not prices:
            return {"week_52_low": 0, "week_52_high": 0}
        return {
            "week_52_low": round(min(prices), 2),
            "week_52_high": round(max(prices), 2),
        }

    async def calculate_relative_strength(self, sector_symbol: str, benchmark_symbol: str = "SPY") -> float:
        sector_hist = await self._run(_download_history, sector_symbol, "2mo")
        bench_hist = await self._run(_download_history, benchmark_symbol, "2mo")
        if len(sector_hist) < 22 or len(bench_hist) < 22:
            return 0.0
        try:
            s_ret = (sector_hist[-1]["close"] - sector_hist[-22]["close"]) / sector_hist[-22]["close"] * 100
            b_ret = (bench_hist[-1]["close"] - bench_hist[-22]["close"]) / bench_hist[-22]["close"] * 100
            return round(s_ret - b_ret, 2)
        except (ZeroDivisionError, IndexError):
            return 0.0

    async def fetch_historical(self, symbol: str, limit: int = 30) -> list[dict]:
        period = "6mo" if limit > 60 else "2mo" if limit > 30 else "1mo"
        history = await self._run(_download_history, symbol, period)
        # Return newest-first, limited
        history.reverse()
        return history[:limit]

    async def fetch_sector_stocks(self, symbols: list[str]) -> list[dict]:
        quotes = await self._run(_download_quotes, symbols, "5d")
        names = await self._run(_fetch_short_names, symbols)
        results = []
        for sym in symbols:
            q = quotes.get(sym)
            if not q:
                continue
            close = q["close"]
            change_p = q["change_p"]
            volume = q["volume"]
            # Skip NaN values
            if close != close or change_p != change_p:
                continue
            if volume != volume:
                volume = 0
            results.append({
                "symbol": sym,
                "name": names.get(sym, sym),
                "close": close,
                "change_p": change_p,
                "volume": volume,
                "market_cap": volume * close,
            })
        return results

    async def close(self) -> None:
        pass
