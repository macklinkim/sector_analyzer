# backend/app/agents/news_agent.py
import json
import logging

import anthropic
from langchain_core.runnables import RunnableConfig

from app.agents.state import MarketAnalysisState, NewsData
from app.config import Settings
from app.services.newsapi import NewsAPIService
from app.services.reliefweb import fetch_world_headlines, filter_crises_with_ai
from app.services.rss_fallback import RSSFallbackService

logger = logging.getLogger(__name__)

NEWS_ANALYSIS_PROMPT = """미국 주식 시장 전문 이코노미스트로서 아래 영어 뉴스를 분석하세요.

## 제외 규칙 (결과에 포함 금지)
연예/가십, 게임, 스포츠, 단순 제품 리뷰/디자인, 라이프스타일, 시장과 무관한 사회면 기사.

## 영향력 점수 (1~10)
- 변동성: 즉각적 주가/원자재 영향 (전쟁/금리 +3)
- 지속성: 1년 이상 산업 지형 변화 (신약/기술 패러다임 +2)
- 신뢰도: FT/WSJ/Reuters/Bloomberg +1, 타블로이드 -1

## 분석 필드
- summary_ko: 한글 1~2문장
- expert_insight: 시장 시그널 + 수혜/타격 섹터 (1~2문장)
- action_item: 모니터링 지표 또는 관련 티커

## 응답 (JSON만)
[{{"index": 1, "summary_ko": "요약", "impact": "긍정|부정|중립", "impact_score": 7, "sector": "섹터", "expert_insight": "통찰", "action_item": "항목"}}]

## 뉴스 목록
{titles_text}"""


async def _analyze_news_with_ai(
    articles: list[dict], settings: Settings
) -> list[dict]:
    """Batch-analyze news articles with Claude and return enriched summaries."""
    if not articles:
        return []

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    titles_text = "\n".join(
        f"{i+1}. [{a.get('category','')}] {a.get('title','')} - "
        f"{a.get('source', {}).get('name', '') if isinstance(a.get('source'), dict) else str(a.get('source', ''))} "
        f"| {a.get('description','') or a.get('summary','') or ''}"
        for i, a in enumerate(articles)
    )

    prompt = NEWS_ANALYSIS_PROMPT.format(titles_text=titles_text)

    raw = ""
    summaries: list[dict] = []
    try:
        # Log prompt so we can inspect what we're sending to Haiku.
        logger.info(
            "News AI prompt preview (model=%s, chars=%d): %s",
            settings.claude_model_news, len(prompt), prompt[:600],
        )
        response = client.messages.create(
            model=settings.claude_model_news,
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            try:
                summaries = json.loads(raw[start:end])
            except json.JSONDecodeError as je:
                logger.error(
                    "News AI JSON parse failed: %s — raw (first 800 chars): %s",
                    je, raw[:800],
                )
        else:
            logger.error(
                "News AI response missing JSON array brackets — raw (first 800 chars): %s",
                raw[:800],
            )
    except Exception as e:
        logger.error("News AI analysis failed (%d articles): %s", len(articles), e)

    if not summaries:
        logger.warning(
            "News AI analysis produced 0 summaries from %d articles — skipping DB save for these rows",
            len(articles),
        )

    # Build keyed map; only articles the AI actually analyzed end up in the DB.
    # DISCARDed or unanalyzed articles are dropped (was the source of the null-field noise).
    summary_map = {s["index"]: s for s in summaries if isinstance(s, dict) and "index" in s}
    seen_urls: set[str] = set()
    result: list[dict] = []
    dropped_discard = 0
    for i, article in enumerate(articles):
        s = summary_map.get(i + 1)
        if s is None:
            dropped_discard += 1
            continue
        url = article.get("url", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        result.append({
            "article_url": url,
            "category": article.get("category", ""),
            "title": article.get("title", ""),
            "source": (
                article.get("source", {}).get("name", "")
                if isinstance(article.get("source"), dict)
                else str(article.get("source", ""))
            ),
            "news_category": None,
            "summary_ko": s.get("summary_ko"),
            "impact_label": s.get("impact"),
            "impact_score": s.get("impact_score", 0),
            "related_sector": s.get("sector"),
            "expert_insight": s.get("expert_insight"),
            "action_item": s.get("action_item"),
        })

    if dropped_discard:
        logger.info(
            "News AI kept %d summaries, dropped %d (DISCARD or unanalyzed)",
            len(result), dropped_discard,
        )
    return result


async def news_agent_node(state: MarketAnalysisState, config: RunnableConfig) -> dict:
    """LangGraph node: collect news from NewsAPI or RSS fallback, then AI-analyze."""
    logger.info("News Agent: collecting news (batch=%s)", state["batch_type"])

    try:
        settings = config.get("configurable", {}).get("settings")
    except Exception:
        settings = None
    if settings is None:
        settings = Settings()

    fallback_used = False
    articles_by_category: dict[str, list[dict]] = {}

    # --- Step 1: Collect news ---
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

    # --- Step 2: AI-analyze news summaries ---
    import asyncio as _asyncio
    all_articles = [a for articles in articles_by_category.values() for a in articles]
    article_summaries = await _analyze_news_with_ai(all_articles, settings)
    logger.info("News Agent: AI-analyzed %d articles → %d summaries", len(all_articles), len(article_summaries))

    await _asyncio.sleep(10)  # Rate limit: 10s between AI calls

    # --- Step 3: Fetch & filter global crises ---
    global_crises: list[dict] = []
    try:
        headlines = await fetch_world_headlines(limit=20)
        await _asyncio.sleep(5)  # Rate limit: 5s before AI crisis filtering
        global_crises = await filter_crises_with_ai(headlines, settings)
        logger.info("News Agent: filtered %d global crises", len(global_crises))
    except Exception as e:
        logger.warning("Global crises fetch failed: %s", e)

    news_data = NewsData(
        articles_by_category=articles_by_category,
        article_summaries=article_summaries,
        global_crises=global_crises,
    )
    return {"news_data": news_data, "news_fallback_used": fallback_used}
