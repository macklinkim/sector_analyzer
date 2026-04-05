"""NewsAPI MCP Server - wraps NewsAPI.org for use as an agent tool."""
import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("newsapi")

NEWSAPI_BASE_URL = "https://newsapi.org/v2"


def _get_api_key() -> str:
    key = os.environ.get("NEWSAPI_KEY", "")
    if not key:
        raise ValueError("NEWSAPI_KEY environment variable is not set")
    return key


@mcp.tool()
async def get_top_headlines(
    category: str = "business",
    country: str = "us",
    page_size: int = 5,
) -> str:
    """Fetch top news headlines by category from NewsAPI.

    Args:
        category: News category (business, technology, science, general, health, sports, entertainment)
        country: Country code (default: us)
        page_size: Number of results (default: 5, max: 100)
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            f"{NEWSAPI_BASE_URL}/top-headlines",
            params={"apiKey": _get_api_key(), "category": category, "country": country, "pageSize": page_size},
        )
        resp.raise_for_status()
        data = resp.json()

    articles = data.get("articles", [])
    results = []
    for a in articles:
        results.append({
            "title": a.get("title", ""),
            "source": a.get("source", {}).get("name", ""),
            "url": a.get("url", ""),
            "publishedAt": a.get("publishedAt", ""),
            "description": a.get("description", ""),
        })
    return json.dumps(results, ensure_ascii=False)


@mcp.tool()
async def search_news(
    query: str,
    from_date: str = "",
    to_date: str = "",
    page_size: int = 5,
) -> str:
    """Search news articles by keyword.

    Args:
        query: Search keyword
        from_date: Start date (YYYY-MM-DD format, optional)
        to_date: End date (YYYY-MM-DD format, optional)
        page_size: Number of results (default: 5)
    """
    params = {"apiKey": _get_api_key(), "q": query, "pageSize": page_size, "language": "en"}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f"{NEWSAPI_BASE_URL}/everything", params=params)
        resp.raise_for_status()
        data = resp.json()

    articles = data.get("articles", [])
    results = []
    for a in articles:
        results.append({
            "title": a.get("title", ""),
            "source": a.get("source", {}).get("name", ""),
            "url": a.get("url", ""),
            "publishedAt": a.get("publishedAt", ""),
            "description": a.get("description", ""),
        })
    return json.dumps(results, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
