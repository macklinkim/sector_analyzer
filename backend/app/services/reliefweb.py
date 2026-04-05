"""ReliefWeb API client for fetching ongoing global crises."""
import json
import logging

import httpx
from anthropic import AsyncAnthropic

from app.config import Settings

logger = logging.getLogger(__name__)

RELIEFWEB_API = "https://api.reliefweb.int/v1/disasters"


async def fetch_current_crises(limit: int = 20) -> list[dict]:
    """Fetch currently ongoing disasters from ReliefWeb API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            RELIEFWEB_API,
            params={
                "appname": "economi-analyzer",
                "filter[field]": "status",
                "filter[value]": "current",
                "sort[]": "date.created:desc",
                "limit": limit,
                "fields[include][]": ["name", "description", "date", "type", "country", "status"],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])


async def filter_crises_with_ai(raw_crises: list[dict], settings: Settings) -> list[dict]:
    """Use Claude to filter and summarize crises for market impact."""
    if not raw_crises:
        return []

    # Prepare concise input for LLM
    crisis_list = []
    for item in raw_crises:
        fields = item.get("fields", {})
        crisis_list.append({
            "name": fields.get("name", "Unknown"),
            "type": [t.get("name", "") for t in fields.get("type", [])],
            "country": [c.get("name", "") for c in fields.get("country", [])],
            "date_created": fields.get("date", {}).get("created", ""),
        })

    prompt = f"""아래는 UN ReliefWeb에서 수집한 현재 진행 중인 글로벌 위기 목록입니다.

{json.dumps(crisis_list, ensure_ascii=False, indent=2)}

위 목록에서 **글로벌 주식 시장, 공급망, 원자재 가격, 또는 거시 경제에 미치는 파급력이 가장 큰 사건 4~5개**만 엄선하세요.
단순 국지적 자연재해는 후순위로 배제하세요.

선별된 사건 각각에 대해 아래 JSON 배열 형식으로만 응답하세요 (다른 텍스트 없이 JSON만):

[
  {{
    "title": "사건 제목 (한글, 간결하게)",
    "source": "ReliefWeb / UN",
    "time_ago": "진행 중 (Ongoing)",
    "summary": "1~2줄 이내 한글 요약. 주식 시장 영향 중심으로 작성.",
    "impact_score": 1~10 정수,
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

        # Extract JSON from response
        if text.startswith("["):
            return json.loads(text)
        # Try to find JSON array in response
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        logger.warning("AI response not valid JSON: %s", text[:200])
        return []
    except Exception as e:
        logger.error("Failed to filter crises with AI: %s", e)
        return []
