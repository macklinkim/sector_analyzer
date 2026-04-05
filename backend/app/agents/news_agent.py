# backend/app/agents/news_agent.py
import logging

from langchain_core.runnables import RunnableConfig

from app.agents.state import MarketAnalysisState, NewsData
from app.services.newsapi import NewsAPIService
from app.services.rss_fallback import RSSFallbackService
from app.config import Settings

logger = logging.getLogger(__name__)


async def news_agent_node(state: MarketAnalysisState, config: RunnableConfig) -> dict:
    """LangGraph node: collect news from NewsAPI or RSS fallback."""
    logger.info("News Agent: collecting news (batch=%s)", state["batch_type"])

    try:
        settings = config.get("configurable", {}).get("settings")
    except Exception:
        settings = None
    if settings is None:
        settings = Settings()

    fallback_used = False
    articles_by_category: dict[str, list[dict]] = {}

    newsapi = NewsAPIService(settings)
    try:
        articles_by_category = await newsapi.fetch_all_categories(top_n=3)
        logger.info("News Agent: collected %d categories via NewsAPI", len(articles_by_category))
    except Exception as e:
        logger.warning("NewsAPI failed: %s. Falling back to RSS.", e)
        fallback_used = True

        rss = RSSFallbackService()
        rss_articles = rss.fetch_news(top_n=12)

        if rss_articles:
            categories = ["politics", "business", "society", "world"]
            per_category = max(1, len(rss_articles) // len(categories))
            for i, cat in enumerate(categories):
                start = i * per_category
                end = start + per_category
                articles_by_category[cat] = rss_articles[start:end]
            logger.info("News Agent: collected %d articles via RSS fallback", len(rss_articles))
        else:
            logger.error("News Agent: both NewsAPI and RSS failed")
            for cat in ["politics", "business", "society", "world"]:
                articles_by_category[cat] = []
    finally:
        await newsapi.close()

    news_data = NewsData(articles_by_category=articles_by_category, article_summaries=[])
    return {"news_data": news_data, "news_fallback_used": fallback_used}
