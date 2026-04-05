import httpx

from app.config import Settings

SECTOR_ETFS = [
    ("Financials", "XLF"),
    ("Real Estate", "XLRE"),
    ("Technology", "XLK"),
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
            quote = await self.fetch_realtime_quote(f"{symbol}.US")
            results.append({
                "symbol": symbol,
                "name": name,
                "close": quote.get("close", 0),
                "change_p": quote.get("change_p", 0),
            })
        return results

    async def calculate_momentum(self, symbol: str) -> dict:
        history = await self.fetch_historical(symbol, limit=180)
        if not history:
            return {"momentum_1w": 0, "momentum_1m": 0, "momentum_3m": 0, "momentum_6m": 0}

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
        }

    async def close(self) -> None:
        await self.client.aclose()
