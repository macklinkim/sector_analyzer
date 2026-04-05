import logging
from datetime import datetime, timezone

import feedparser

logger = logging.getLogger(__name__)

GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
GOOGLE_NEWS_BUSINESS_RSS = "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en"


class RSSFallbackService:
    def fetch_news(self, top_n: int = 12) -> list[dict]:
        feed = feedparser.parse(GOOGLE_NEWS_BUSINESS_RSS)

        if feed.bozo:
            logger.warning("RSS feed parse error: %s", feed.bozo_exception)
            return []

        articles = []
        for entry in feed.entries[:top_n]:
            source_name = "Unknown"
            if hasattr(entry, "source") and hasattr(entry.source, "title"):
                source_name = entry.source.title

            articles.append({
                "title": entry.title,
                "url": entry.link,
                "published": entry.published if hasattr(entry, "published") else "",
                "source": source_name,
            })

        return articles
