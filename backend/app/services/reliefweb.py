"""Global crises extraction from news data using Claude AI."""
import json
import logging

import httpx
import feedparser
from anthropic import AsyncAnthropic

from app.config import Settings

logger = logging.getLogger(__name__)

# Google News RSS for world/geopolitical events
GOOGLE_NEWS_WORLD_RSS = "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB"


async def fetch_world_headlines(limit: int = 20) -> list[dict]:
    """Fetch world news headlines from Google News RSS."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; SectorAnalyzer/1.0)"}
        async with httpx.AsyncClient(timeout=15.0) as client:
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

    prompt = f"""아래는 최근 글로벌 뉴스 헤드라인 목록입니다.

{headlines_text}

위 헤드라인에서 **현재 진행 중인 글로벌 핵심 위기(Ongoing Crises)** 중 주식 시장, 공급망, 원자재 가격, 거시 경제에 파급력이 큰 사건 4~5개를 엄선하세요.

단순 국내 뉴스, 스포츠, 연예 등은 배제하세요.
지정학적 분쟁, 무역전쟁, 에너지 위기, 전쟁, 제재 등을 우선하세요.

반드시 아래 JSON 배열 형식으로만 응답하세요 (다른 텍스트 없이 JSON만):

[
  {{
    "title": "사건 제목 (한글, 간결하게)",
    "source": "출처 매체명",
    "time_ago": "진행 중 (Ongoing)",
    "summary": "1~2줄 이내 한글 요약. 주식 시장 영향 중심.",
    "impact_score": 1에서10사이 정수,
    "affected_sector": "영향받는 섹터명 (에너지, 항공우주/국방, 산업재, 금융 등)",
    "sentiment": "negative 또는 neutral 또는 positive"
  }}
]"""

    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
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
