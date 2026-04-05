import pytest
from unittest.mock import patch, MagicMock


MOCK_RSS_FEED = MagicMock()
MOCK_RSS_FEED.entries = [
    MagicMock(
        title="Economy News 1",
        link="https://news.google.com/1",
        published="Sat, 05 Apr 2026 08:00:00 GMT",
        source=MagicMock(title="Reuters"),
    ),
    MagicMock(
        title="Economy News 2",
        link="https://news.google.com/2",
        published="Sat, 05 Apr 2026 07:00:00 GMT",
        source=MagicMock(title="AP"),
    ),
    MagicMock(
        title="Economy News 3",
        link="https://news.google.com/3",
        published="Sat, 05 Apr 2026 06:00:00 GMT",
        source=MagicMock(title="CNBC"),
    ),
]
MOCK_RSS_FEED.bozo = False


def test_fetch_google_news_rss():
    from app.services.rss_fallback import RSSFallbackService

    with patch("app.services.rss_fallback.feedparser.parse", return_value=MOCK_RSS_FEED):
        service = RSSFallbackService()
        articles = service.fetch_news(top_n=3)
        assert len(articles) == 3
        assert articles[0]["title"] == "Economy News 1"
        assert articles[0]["source"] == "Reuters"


def test_handles_empty_feed():
    from app.services.rss_fallback import RSSFallbackService

    empty_feed = MagicMock()
    empty_feed.entries = []
    empty_feed.bozo = False

    with patch("app.services.rss_fallback.feedparser.parse", return_value=empty_feed):
        service = RSSFallbackService()
        articles = service.fetch_news()
        assert articles == []


def test_handles_parse_error():
    from app.services.rss_fallback import RSSFallbackService

    error_feed = MagicMock()
    error_feed.entries = []
    error_feed.bozo = True
    error_feed.bozo_exception = Exception("Parse error")

    with patch("app.services.rss_fallback.feedparser.parse", return_value=error_feed):
        service = RSSFallbackService()
        articles = service.fetch_news()
        assert articles == []
