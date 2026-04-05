import httpx
from app.config import Settings

NEWSAPI_BASE_URL = "https://newsapi.org/v2"

CATEGORY_MAP = {
    "politics": "general",
    "business": "business",
    "society": "science",
    "world": "technology",
}


class NewsAPIService:
    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.newsapi_key
        self.client = httpx.AsyncClient(timeout=15.0)

    async def fetch_top_headlines(self, category: str, country: str = "us", page_size: int = 5) -> list[dict]:
        resp = await self.client.get(
            f"{NEWSAPI_BASE_URL}/top-headlines",
            params={
                "apiKey": self.api_key,
                "category": category,
                "country": country,
                "pageSize": page_size,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("articles", [])

    async def fetch_all_categories(self, top_n: int = 3) -> dict[str, list[dict]]:
        results = {}
        for label, api_category in CATEGORY_MAP.items():
            articles = await self.fetch_top_headlines(api_category, page_size=top_n)
            results[label] = articles[:top_n]
        return results

    async def close(self) -> None:
        await self.client.aclose()
