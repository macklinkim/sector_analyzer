# backend/app/agents/news_agent.py
import json
import logging

from anthropic import AsyncAnthropic
from langchain_core.runnables import RunnableConfig

from app.agents.state import MarketAnalysisState, NewsData
from app.config import Settings
from app.services.newsapi import NewsAPIService
from app.services.reliefweb import fetch_world_headlines, filter_crises_with_ai
from app.services.rss_fallback import RSSFallbackService

logger = logging.getLogger(__name__)

NEWS_ANALYSIS_PROMPT = """당신은 미국 주식 시장 전문 이코노미스트입니다. 아래 영어 뉴스 기사를 분석하세요.

## 분류 규칙 (Classification)
각 뉴스를 아래 카테고리로 분류하세요. DISCARD 뉴스는 결과에서 완전히 제외하세요.

- **A_MACRO**: 전쟁, 에너지 위기, 금리/통화 정책, 대선 후보 발언, 국제기구(IEA/IMF/Fed) 경고, 지정학적 갈등
- **B_INDUSTRY**: 산업 규제 변화, 파괴적 의료/과학 발견, 핵심 기술 인프라(양자/우주/AI), 대형 M&A
- **C_CORPORATE**: 빅테크 생태계 변화, 기업 실적 직결 서비스 변경, 주요 기업 경영진 교체
- **DISCARD**: 연예/가십, 게임 이벤트/리뷰, 스포츠, 단순 디자인 변경, 개인적 사용 후기, 시장과 무관한 사회면 기사

## 영향력 점수 산출 기준 (1~10)
- **변동성(Volatility):** 즉각적 주가/원자재 가격 영향 여부 (전쟁 위협 +3점, 금리 결정 +3점)
- **지속성(Persistence):** 1년 이상 장기적 산업 지형 변화 여부 (신약 승인 +2점, 기술 패러다임 +2점)
- **신뢰도(Authority):** FT, WSJ, Reuters, Bloomberg = 가중치 +1점 / 타블로이드, 블로그 = -1점

## 분석 요구사항
각 뉴스에 대해:
1. **summary_ko**: 한글 1~2문장 핵심 요약
2. **expert_insight**: "이 뉴스가 시장에 주는 시그널" + "수혜/타격 섹터" 관점의 전문가적 통찰 (1~2문장)
3. **action_item**: 모니터링해야 할 지표 또는 관련 티커 (예: "WTI 선물 추이 확인", "XLE/XOM 주가 반응 관찰")

## 응답 형식
반드시 아래 JSON 배열 형식으로만 응답하세요. DISCARD 뉴스는 제외. 다른 텍스트 없이 JSON만:
[{{"index": 1, "news_category": "A_MACRO|B_INDUSTRY|C_CORPORATE", "summary_ko": "한글요약", "impact": "긍정|부정|중립", "impact_score": 7, "sector": "관련섹터", "expert_insight": "전문가 통찰", "action_item": "모니터링 항목"}}]

## 뉴스 목록
{titles_text}"""


async def _analyze_news_with_ai(
    articles: list[dict], settings: Settings
) -> list[dict]:
    """Batch-analyze news articles with Claude and return enriched summaries."""
    if not articles:
        return []

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    titles_text = "\n".join(
        f"{i+1}. [{a.get('category','')}] {a.get('title','')} - "
        f"{a.get('source', {}).get('name', '') if isinstance(a.get('source'), dict) else str(a.get('source', ''))} "
        f"| {a.get('description','') or a.get('summary','') or ''}"
        for i, a in enumerate(articles)
    )

    prompt = NEWS_ANALYSIS_PROMPT.format(titles_text=titles_text)

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            summaries = json.loads(raw[start:end])
        else:
            summaries = []
    except Exception as e:
        logger.error("News AI analysis failed: %s", e)
        summaries = []

    # Merge summaries back with article metadata
    summary_map = {s["index"]: s for s in summaries if isinstance(s, dict)}
    result: list[dict] = []
    for i, article in enumerate(articles):
        s = summary_map.get(i + 1, {})
        url = article.get("url", "")
        result.append({
            "article_url": url,
            "category": article.get("category", ""),
            "title": article.get("title", ""),
            "source": (
                article.get("source", {}).get("name", "")
                if isinstance(article.get("source"), dict)
                else str(article.get("source", ""))
            ),
            "news_category": s.get("news_category"),
            "summary_ko": s.get("summary_ko"),
            "impact_label": s.get("impact"),
            "impact_score": s.get("impact_score", 0),
            "related_sector": s.get("sector"),
            "expert_insight": s.get("expert_insight"),
            "action_item": s.get("action_item"),
        })

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
    all_articles = [a for articles in articles_by_category.values() for a in articles]
    article_summaries = await _analyze_news_with_ai(all_articles, settings)
    logger.info("News Agent: AI-analyzed %d articles → %d summaries", len(all_articles), len(article_summaries))

    # --- Step 3: Fetch & filter global crises ---
    global_crises: list[dict] = []
    try:
        headlines = await fetch_world_headlines(limit=20)
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
