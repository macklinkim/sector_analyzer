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


@router.get("/summaries")
async def get_news_summaries(limit: int = Query(10, ge=1, le=20)):
    """Get news articles with AI-generated Korean summaries and expert analysis."""
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
        f"{i+1}. [{a.get('category','')}] {a.get('title','')} - {a.get('source', '')} | {a.get('summary','') or ''}"
        for i, a in enumerate(articles)
    )

    prompt = NEWS_ANALYSIS_PROMPT.format(titles_text=titles_text)

    try:
        response = client.messages.create(
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
    except Exception:
        summaries = []

    # Merge summaries with articles, skip DISCARD
    summary_map = {s["index"]: s for s in summaries if isinstance(s, dict)}
    result = []
    for i, article in enumerate(articles):
        s = summary_map.get(i + 1, {})
        # Skip if not in summary (DISCARD by AI)
        if not s and i + 1 not in summary_map:
            # Still include but with no enrichment
            result.append({
                **article,
                "summary_ko": None,
                "impact_label": None,
                "impact_score": 0,
                "related_sector": None,
                "news_category": None,
                "expert_insight": None,
                "action_item": None,
            })
            continue
        result.append({
            **article,
            "summary_ko": s.get("summary_ko"),
            "impact_label": s.get("impact"),
            "impact_score": s.get("impact_score", 0),
            "related_sector": s.get("sector"),
            "news_category": s.get("news_category"),
            "expert_insight": s.get("expert_insight"),
            "action_item": s.get("action_item"),
        })

    # Sort: high impact first, DISCARD (no category) last
    result.sort(key=lambda x: (x.get("impact_score") or 0), reverse=True)

    return result


@router.get("/crises")
async def get_global_crises():
    """Fetch ongoing global crises, filtered by AI for market impact."""
    import time

    from app.config import Settings
    from app.services.reliefweb import fetch_world_headlines, filter_crises_with_ai

    # In-memory cache (1 hour)
    cache_key = "_crises_cache"
    cache = getattr(get_global_crises, cache_key, None)
    if cache:
        ts, data = cache
        if time.time() - ts < 3600:
            return data

    settings = Settings()
    headlines = await fetch_world_headlines(limit=20)
    filtered = await filter_crises_with_ai(headlines, settings)

    # Cache result
    setattr(get_global_crises, cache_key, (time.time(), filtered))

    return filtered
