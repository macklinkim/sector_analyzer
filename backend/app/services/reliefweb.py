"""Global crises extraction from news data using Claude AI."""
import json
import logging

import httpx
import feedparser
import anthropic

from app.config import Settings

logger = logging.getLogger(__name__)

# Google News RSS for world/geopolitical events
GOOGLE_NEWS_WORLD_RSS = "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB"


async def fetch_world_headlines(limit: int = 20) -> list[dict]:
    """Fetch world news headlines from Google News RSS."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SectorAnalyzer/1.0)"}
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(GOOGLE_NEWS_WORLD_RSS, headers=headers)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
            items = []
            for entry in feed.entries[:limit]:
                items.append({
                    "title": entry.get("title", ""),
                    "source": entry.get("source", {}).get("title", "") if hasattr(entry.get("source", {}), "get") else "",
                    "published": entry.get("published", ""),
                    "link": entry.get("link", ""),
                })
            logger.info("Fetched %d world headlines from Google News RSS", len(items))
            return items
    except Exception as e:
        logger.warning("Failed to fetch world headlines: %s", e)
        return []


async def filter_crises_with_ai(headlines: list[dict], settings: Settings) -> list[dict]:
    """Use Claude to identify ongoing global crises with market impact."""
    if not headlines:
        return []

    headlines_text = json.dumps(headlines, ensure_ascii=False, indent=2)

    prompt = f"""아래 글로벌 뉴스 헤드라인에서 **현재 진행 중인 위기(Ongoing Crises) 5~7건**을 선별하세요.

## 선별 우선순위 (순서대로)
1. **직접 전쟁/무력충돌** — 사상자 발생, 공격·점령·폭격 뉴스 (예: 우크라이나 공격, 이스라엘-헤즈볼라 충돌). 헤드라인에 있다면 반드시 포함.
2. **에너지/해운 위기** — 해협 봉쇄, 유조선 공격, 파이프라인 차단
3. **경제 제재·무역전쟁·지정학 분쟁** — 관세 보복, 국가간 갈등
4. **주요 국방/공급망 뉴스** — 대형 방산계약, 핵심 광물·반도체 차단

## 제약
- 국내 정치 선거/스포츠/연예/단신/축제는 제외
- 지역 다양성 확보: 중동·유럽·아시아 각 권역에서 가능한 한 1건 이상 포함
- 활동 중인 전쟁(우크라이나, 중동) 헤드라인이 존재하면 경제 뉴스만 고르지 말 것
- 이미 완전히 종결된 사건은 제외

## 헤드라인
{headlines_text}

## 응답 (JSON 배열만, 다른 텍스트 금지)
[
  {{
    "title": "사건 제목 (한글, 간결하게)",
    "source": "출처 매체명",
    "time_ago": "진행 중 (Ongoing)",
    "summary": "1~2줄 한글 요약 (주식/원자재 영향 포함)",
    "impact_score": 1에서10사이 정수,
    "affected_sector": "에너지 | 항공우주/국방 | 산업재 | 금융 | 공급망 | 원자재 등",
    "sentiment": "negative | neutral | positive"
  }}
]"""

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    try:
        logger.info(
            "Crisis AI prompt preview (model=%s, chars=%d): %s",
            settings.claude_model_crisis, len(prompt), prompt[:600],
        )
        response = client.messages.create(
            model=settings.claude_model_crisis,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()

        # Extract JSON array
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        logger.warning("AI response not valid JSON: %s", text[:200])
        return []
    except Exception as e:
        logger.error("Failed to filter crises with AI: %s", e)
        return []
