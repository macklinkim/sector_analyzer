# backend/tests/agents/test_news_agent.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

MOCK_ARTICLES = {
    "politics": [{"title": "News 1", "url": "http://1", "source": {"name": "R"}, "publishedAt": "2026-04-05T08:00:00Z", "description": "desc"}],
    "business": [{"title": "News 2", "url": "http://2", "source": {"name": "C"}, "publishedAt": "2026-04-05T08:00:00Z", "description": "desc"}],
    "society": [{"title": "News 3", "url": "http://3", "source": {"name": "A"}, "publishedAt": "2026-04-05T08:00:00Z", "description": "desc"}],
    "world": [{"title": "News 4", "url": "http://4", "source": {"name": "B"}, "publishedAt": "2026-04-05T08:00:00Z", "description": "desc"}],
}


@pytest.fixture
def mock_newsapi_service():
    service = AsyncMock()
    service.fetch_all_categories.return_value = MOCK_ARTICLES
    service.close = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_news_agent_collects_articles(mock_newsapi_service):
    from app.agents.news_agent import news_agent_node
    from app.agents.state import create_initial_state, MarketData

    state = create_initial_state("pre_market")
    state["market_data"] = MarketData()

    with patch("app.agents.news_agent.NewsAPIService", return_value=mock_newsapi_service):
        result = await news_agent_node(state, MagicMock())
        assert result["news_data"] is not None
        assert len(result["news_data"].articles_by_category) == 4
        assert result["news_fallback_used"] is False


@pytest.mark.asyncio
async def test_news_agent_falls_back_to_rss():
    from app.agents.news_agent import news_agent_node
    from app.agents.state import create_initial_state, MarketData

    state = create_initial_state("pre_market")
    state["market_data"] = MarketData()

    mock_newsapi = AsyncMock()
    mock_newsapi.fetch_all_categories.side_effect = Exception("Rate limit")
    mock_newsapi.close = AsyncMock()

    mock_rss = MagicMock()
    mock_rss.fetch_news.return_value = [
        {"title": "RSS News", "url": "http://rss1", "source": "Reuters", "published": "2026-04-05"},
    ]

    with patch("app.agents.news_agent.NewsAPIService", return_value=mock_newsapi), \
         patch("app.agents.news_agent.RSSFallbackService", return_value=mock_rss):
        result = await news_agent_node(state, MagicMock())
        assert result["news_fallback_used"] is True
        assert result["news_data"] is not None
