import pytest
from unittest.mock import AsyncMock, MagicMock, patch

MOCK_NEWSAPI_RESPONSE = {
    "status": "ok",
    "totalResults": 3,
    "articles": [
        {
            "title": "Fed Decision Today",
            "source": {"name": "Reuters"},
            "url": "https://reuters.com/1",
            "publishedAt": "2026-04-05T08:00:00Z",
            "description": "Federal Reserve meeting today...",
        },
        {
            "title": "Tech Earnings Beat",
            "source": {"name": "CNBC"},
            "url": "https://cnbc.com/2",
            "publishedAt": "2026-04-05T07:00:00Z",
            "description": "Major tech companies beat...",
        },
        {
            "title": "Oil Prices Surge",
            "source": {"name": "Bloomberg"},
            "url": "https://bloomberg.com/3",
            "publishedAt": "2026-04-05T06:00:00Z",
            "description": "Oil prices surge on...",
        },
    ],
}


@pytest.fixture
def newsapi_service(mock_settings):
    from app.services.newsapi import NewsAPIService
    return NewsAPIService(mock_settings)


@pytest.mark.asyncio
async def test_fetch_top_headlines(newsapi_service):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_NEWSAPI_RESPONSE
    mock_response.raise_for_status = MagicMock()

    with patch.object(newsapi_service.client, "get", new_callable=AsyncMock, return_value=mock_response):
        articles = await newsapi_service.fetch_top_headlines("business")
        assert len(articles) == 3
        assert articles[0]["title"] == "Fed Decision Today"


@pytest.mark.asyncio
async def test_fetch_all_categories(newsapi_service):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_NEWSAPI_RESPONSE
    mock_response.raise_for_status = MagicMock()

    with patch.object(newsapi_service.client, "get", new_callable=AsyncMock, return_value=mock_response):
        result = await newsapi_service.fetch_all_categories(top_n=3)
        assert len(result) == 4
        for category, articles in result.items():
            assert len(articles) <= 3


@pytest.mark.asyncio
async def test_handles_rate_limit(newsapi_service):
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.raise_for_status.side_effect = Exception("Rate limit exceeded")

    with patch.object(newsapi_service.client, "get", new_callable=AsyncMock, return_value=mock_response):
        with pytest.raises(Exception, match="Rate limit"):
            await newsapi_service.fetch_top_headlines("business")
