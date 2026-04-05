import httpx

from app.config import Settings

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
    ("S&P 500", "SPY"),
    ("NASDAQ", "QQQ"),
    ("DOW", "DIA"),
    ("KOSDAQ", "2001.KO"),
]

# 거시 경제 지표 심볼 (EODHD)
MACRO_INDICATORS = [
    ("US 10Y Treasury", "US10Y.INDX"),
    ("DXY Dollar Index", "DX-Y.NYB"),
    ("WTI Crude Oil", "CL.COMM"),
    ("Gold", "GC.COMM"),
]


class EODHDService:
    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.eodhd_api_key
        self.base_url = settings.eodhd_base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch_realtime_quote(self, symbol: str) -> dict:
        resp = await self.client.get(
            f"{self.base_url}/real-time/{symbol}",
            params={"api_token": self.api_key, "fmt": "json"},
        )
        resp.raise_for_status()
        return resp.json()

    async def fetch_historical(self, symbol: str, period: str = "d", limit: int = 180) -> list[dict]:
        resp = await self.client.get(
            f"{self.base_url}/eod/{symbol}",
            params={
                "api_token": self.api_key,
                "fmt": "json",
                "period": period,
                "order": "d",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data[:limit]

    async def fetch_sector_etfs(self) -> list[dict]:
        results = []
        for name, symbol in SECTOR_ETFS:
            quote = await self.fetch_realtime_quote(f"{symbol}.US")
            results.append({
                "symbol": symbol,
                "name": name,
                "close": quote.get("close", 0),
                "change_p": quote.get("change_p", 0),
                "volume": quote.get("volume", 0),
            })
        return results

    async def fetch_indices(self) -> list[dict]:
        results = []
        for name, symbol in INDEX_SYMBOLS:
            # Symbol already contains exchange suffix (e.g., "2001.KO") or needs ".US"
            api_symbol = symbol if "." in symbol else f"{symbol}.US"
            try:
                quote = await self.fetch_realtime_quote(api_symbol)
                results.append({
                    "symbol": symbol.split(".")[0] if "." in symbol else symbol,
                    "name": name,
                    "close": quote.get("close", 0),
                    "change_p": quote.get("change_p", 0),
                })
            except Exception:
                # Skip unavailable indices (e.g., KOSDAQ during US hours)
                pass
        return results

    async def calculate_momentum(self, symbol: str) -> dict:
        history = await self.fetch_historical(symbol, limit=260)
        if not history:
            return {"momentum_1w": 0, "momentum_1m": 0, "momentum_3m": 0, "momentum_6m": 0, "momentum_1y": 0}

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

    async def fetch_economic_indicators(self) -> list[dict]:
        """Fetch macro economic indicators: US10Y, DXY, WTI, Gold."""
        results = []
        for name, symbol in MACRO_INDICATORS:
            try:
                quote = await self.fetch_realtime_quote(symbol)
                current = quote.get("close", 0)
                prev = quote.get("previousClose", quote.get("previous_close", 0))
                if prev and current:
                    direction = "up" if current > prev else ("down" if current < prev else "flat")
                else:
                    direction = "flat"
                results.append({
                    "indicator_name": name,
                    "value": current,
                    "previous_value": prev,
                    "change_direction": direction,
                    "source": "EODHD",
                })
            except Exception:
                pass
        return results

    async def calculate_52week_range(self, symbol: str) -> dict:
        """Calculate 52-week high and low from historical data."""
        try:
            history = await self.fetch_historical(symbol, limit=260)
            if not history:
                return {"week_52_low": 0, "week_52_high": 0}
            prices = [d["close"] for d in history if d.get("close")]
            if not prices:
                return {"week_52_low": 0, "week_52_high": 0}
            return {
                "week_52_low": round(min(prices), 2),
                "week_52_high": round(max(prices), 2),
            }
        except Exception:
            return {"week_52_low": 0, "week_52_high": 0}

    async def calculate_relative_strength(self, sector_symbol: str, benchmark_symbol: str = "SPY.US") -> float:
        """Calculate 1-month relative strength vs benchmark (SPY)."""
        try:
            sector_hist = await self.fetch_historical(sector_symbol, limit=25)
            benchmark_hist = await self.fetch_historical(benchmark_symbol, limit=25)
            if len(sector_hist) < 22 or len(benchmark_hist) < 22:
                return 0.0
            sector_ret = (sector_hist[0]["close"] - sector_hist[21]["close"]) / sector_hist[21]["close"] * 100
            bench_ret = (benchmark_hist[0]["close"] - benchmark_hist[21]["close"]) / benchmark_hist[21]["close"] * 100
            return round(sector_ret - bench_ret, 2)
        except Exception:
            return 0.0

    async def close(self) -> None:
        await self.client.aclose()
