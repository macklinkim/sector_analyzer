from fastapi import APIRouter, Depends, Query

from app.api.deps import get_supabase
from app.services.supabase import SupabaseService

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/articles")
def get_news_articles(
    category: str | None = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100),
    svc: SupabaseService = Depends(get_supabase),
):
    if category:
        return svc.get_news_by_category(category, limit=limit)
    return svc.get_latest_news_articles(limit=limit)


@router.get("/impacts")
def get_news_impacts(svc: SupabaseService = Depends(get_supabase)):
    return svc.get_latest_news_impacts()


@router.get("/summaries")
async def get_news_summaries(limit: int = Query(10, ge=1, le=20)):
    """Get news articles with AI-generated Korean summaries."""
    import json
    import anthropic

    from app.config import Settings

    settings = Settings()
    svc = get_supabase()
    articles = svc.get_latest_news_articles(limit=limit)

    if not articles:
        return []

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    titles_text = "\n".join(
        f"{i+1}. [{a.get('category','')}] {a.get('title','')} - {a.get('summary','') or ''}"
        for i, a in enumerate(articles)
    )

    prompt = f"""다음 영어 뉴스 기사 목록을 분석하세요. 각 뉴스에 대해:
1. 한글 1~2문장 요약
2. 미국 주식 섹터에 미치는 영향 평가 (긍정/부정/중립)
3. 영향도 점수 (0~10, 0=무관, 10=매우큰영향)
4. 가장 관련 있는 섹터명

반드시 아래 JSON 배열 형식으로만 응답하세요. 다른 텍스트 없이 JSON만:
[{{"index": 1, "summary_ko": "한글요약", "impact": "긍정", "impact_score": 7, "sector": "기술"}}]

뉴스 목록:
{titles_text}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        summaries = json.loads(response.content[0].text)
    except Exception:
        summaries = []

    # Merge summaries with articles
    summary_map = {s["index"]: s for s in summaries if isinstance(s, dict)}
    result = []
    for i, article in enumerate(articles):
        s = summary_map.get(i + 1, {})
        result.append({
            **article,
            "summary_ko": s.get("summary_ko"),
            "impact_label": s.get("impact"),
            "impact_score": s.get("impact_score", 0),
            "related_sector": s.get("sector"),
        })

    return result
