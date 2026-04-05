# Phase 2: AI Pipeline — LangGraph 에이전트 파이프라인

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** LangGraph 기반 3개 에이전트(Data, News, Analyst) 파이프라인 구현 + NewsAPI MCP 서버 구축. 배치 실행 시 EODHD 데이터 수집 → 뉴스 수집 → AI 분석(4단계 판단) → Supabase 저장까지 E2E 동작.

**Architecture:** LangGraph StateGraph로 3노드 순차 실행. 각 노드는 Phase 1의 서비스 클라이언트를 도구로 사용. Analyst Agent는 Claude API를 통해 Macro Regime Detection → Base Score → Override → Scoring 4단계 수행.

**Tech Stack:** langgraph, langchain, langchain-anthropic, anthropic, mcp (추가 설치)

**Spec:** `docs/superpowers/specs/2026-04-05-market-insights-dashboard-design.md`
**Agents:** `AGENTS.md`
**Strategy:** `docs/sector-rotation-strategy.md`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `backend/pyproject.toml` | AI 패키지 의존성 추가 |
| Create | `backend/app/agents/state.py` | LangGraph 공유 상태 스키마 |
| Create | `backend/app/agents/data_agent.py` | EODHD 데이터 수집 노드 |
| Create | `backend/app/agents/news_agent.py` | 뉴스 수집 노드 (NewsAPI + RSS fallback) |
| Create | `backend/app/agents/analyst_agent.py` | Claude 기반 4단계 분석 노드 |
| Create | `backend/app/agents/graph.py` | LangGraph 메인 그래프 정의 |
| Create | `backend/app/mcp/news_server.py` | NewsAPI MCP 서버 |
| Create | `backend/tests/agents/__init__.py` | 에이전트 테스트 패키지 |
| Create | `backend/tests/agents/test_state.py` | 상태 스키마 테스트 |
| Create | `backend/tests/agents/test_data_agent.py` | Data Agent 테스트 |
| Create | `backend/tests/agents/test_news_agent.py` | News Agent 테스트 |
| Create | `backend/tests/agents/test_analyst_agent.py` | Analyst Agent 테스트 |
| Create | `backend/tests/agents/test_graph.py` | 그래프 통합 테스트 |

---

## Task 1: AI 패키지 의존성 추가

**Files:**
- Modify: `backend/pyproject.toml`

- [ ] **Step 1: pyproject.toml에 AI 의존성 추가**

`dependencies`에 다음 추가:
```toml
    "langgraph>=0.4.0",
    "langchain>=0.3.0",
    "langchain-anthropic>=0.3.0",
    "anthropic>=0.40.0",
```

- [ ] **Step 2: 설치**

```bash
cd backend && .venv/Scripts/pip install -e ".[dev]"
```

- [ ] **Step 3: 테스트 디렉토리 생성**

```bash
mkdir -p backend/tests/agents
touch backend/tests/agents/__init__.py
```

- [ ] **Step 4: 기존 테스트가 깨지지 않는지 확인**

```bash
cd backend && .venv/Scripts/python -m pytest -v --tb=short
```
Expected: 22 passed

- [ ] **Step 5: Commit**

```bash
git add backend/pyproject.toml backend/tests/agents/__init__.py
git commit -m "chore: add LangGraph and Claude API dependencies"
```

---

## Task 2: LangGraph 공유 상태 스키마

**Files:**
- Create: `backend/app/agents/state.py`
- Create: `backend/tests/agents/test_state.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# backend/tests/agents/test_state.py
from datetime import datetime, timezone


def test_create_initial_state():
    from app.agents.state import create_initial_state
    state = create_initial_state("pre_market")
    assert state["batch_type"] == "pre_market"
    assert state["triggered_at"] is not None
    assert state["market_data"] is None
    assert state["news_data"] is None
    assert state["news_fallback_used"] is False
    assert state["analysis_results"] is None


def test_market_data_structure():
    from app.agents.state import MarketData
    data = MarketData(
        indices=[],
        sectors=[],
        economic_indicators=[],
        momentum={},
    )
    assert data.indices == []
    assert data.momentum == {}


def test_news_data_structure():
    from app.agents.state import NewsData
    data = NewsData(
        articles_by_category={},
        article_summaries=[],
    )
    assert data.articles_by_category == {}


def test_analysis_results_structure():
    from app.agents.state import AnalysisResults
    results = AnalysisResults(
        regime=None,
        scoreboards=[],
        rotation_signals=[],
        news_impacts=[],
        report=None,
    )
    assert results.scoreboards == []
```

- [ ] **Step 2: 테스트 실패 확인**

- [ ] **Step 3: state.py 구현**

```python
# backend/app/agents/state.py
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, TypedDict

from app.models.market import MarketIndex, Sector, EconomicIndicator
from app.models.news import NewsArticle, NewsImpactAnalysis
from app.models.analysis import MacroRegime, SectorScoreboard, RotationSignal, MarketReport


@dataclass
class MarketData:
    indices: list[dict] = field(default_factory=list)
    sectors: list[dict] = field(default_factory=list)
    economic_indicators: list[dict] = field(default_factory=list)
    momentum: dict[str, dict] = field(default_factory=dict)  # symbol -> momentum dict


@dataclass
class NewsData:
    articles_by_category: dict[str, list[dict]] = field(default_factory=dict)
    article_summaries: list[dict] = field(default_factory=list)


@dataclass
class AnalysisResults:
    regime: dict | None = None
    scoreboards: list[dict] = field(default_factory=list)
    rotation_signals: list[dict] = field(default_factory=list)
    news_impacts: list[dict] = field(default_factory=list)
    report: dict | None = None


class MarketAnalysisState(TypedDict):
    batch_type: str
    triggered_at: str
    market_data: MarketData | None
    news_data: NewsData | None
    news_fallback_used: bool
    analysis_results: AnalysisResults | None


def create_initial_state(batch_type: str) -> MarketAnalysisState:
    return MarketAnalysisState(
        batch_type=batch_type,
        triggered_at=datetime.now(timezone.utc).isoformat(),
        market_data=None,
        news_data=None,
        news_fallback_used=False,
        analysis_results=None,
    )
```

- [ ] **Step 4: 테스트 통과 확인 (4 passed)**

- [ ] **Step 5: Commit**

```bash
git add backend/app/agents/state.py backend/tests/agents/test_state.py
git commit -m "feat: add LangGraph shared state schema"
```

---

## Task 3: Data Agent 노드

**Files:**
- Create: `backend/app/agents/data_agent.py`
- Create: `backend/tests/agents/test_data_agent.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# backend/tests/agents/test_data_agent.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_eodhd_service():
    service = AsyncMock()
    service.fetch_indices.return_value = [
        {"symbol": "SPY", "name": "S&P 500", "close": 5200.50, "change_p": 0.55},
    ]
    service.fetch_sector_etfs.return_value = [
        {"symbol": "XLK", "name": "Technology", "close": 210.30, "change_p": 1.2, "volume": 50000000},
    ]
    service.calculate_momentum.return_value = {
        "momentum_1w": 2.1, "momentum_1m": 5.3, "momentum_3m": 12.0, "momentum_6m": 18.5,
    }
    return service


@pytest.mark.asyncio
async def test_data_agent_collects_market_data(mock_eodhd_service):
    from app.agents.data_agent import data_agent_node
    from app.agents.state import create_initial_state

    state = create_initial_state("pre_market")

    with patch("app.agents.data_agent.EODHDService", return_value=mock_eodhd_service):
        result = await data_agent_node(state, MagicMock())
        assert result["market_data"] is not None
        assert len(result["market_data"].indices) > 0
        assert len(result["market_data"].sectors) > 0


@pytest.mark.asyncio
async def test_data_agent_calculates_momentum(mock_eodhd_service):
    from app.agents.data_agent import data_agent_node
    from app.agents.state import create_initial_state

    state = create_initial_state("post_market")

    with patch("app.agents.data_agent.EODHDService", return_value=mock_eodhd_service):
        result = await data_agent_node(state, MagicMock())
        assert len(result["market_data"].momentum) > 0
```

- [ ] **Step 2: 테스트 실패 확인**

- [ ] **Step 3: data_agent.py 구현**

```python
# backend/app/agents/data_agent.py
import logging
from typing import Any

from app.agents.state import MarketAnalysisState, MarketData
from app.services.eodhd import EODHDService
from app.config import Settings

logger = logging.getLogger(__name__)


async def data_agent_node(
    state: MarketAnalysisState,
    config: Any,
) -> dict:
    """LangGraph node: collect market data from EODHD API."""
    logger.info("Data Agent: collecting market data (batch=%s)", state["batch_type"])

    settings = config.get("configurable", {}).get("settings") if isinstance(config, dict) else None
    if settings is None:
        settings = Settings()

    service = EODHDService(settings)

    try:
        indices = await service.fetch_indices()
        sectors = await service.fetch_sector_etfs()

        # Calculate momentum for each sector ETF
        momentum = {}
        for sector in sectors:
            symbol = f"{sector['symbol']}.US"
            try:
                m = await service.calculate_momentum(symbol)
                momentum[sector["symbol"]] = m
            except Exception as e:
                logger.warning("Failed to calculate momentum for %s: %s", symbol, e)
                momentum[sector["symbol"]] = {
                    "momentum_1w": 0, "momentum_1m": 0, "momentum_3m": 0, "momentum_6m": 0,
                }

        market_data = MarketData(
            indices=indices,
            sectors=sectors,
            economic_indicators=[],
            momentum=momentum,
        )

        logger.info("Data Agent: collected %d indices, %d sectors", len(indices), len(sectors))
        return {"market_data": market_data}

    except Exception as e:
        logger.error("Data Agent failed: %s", e)
        return {"market_data": MarketData()}
    finally:
        await service.close()
```

- [ ] **Step 4: 테스트 통과 확인 (2 passed)**

- [ ] **Step 5: Commit**

```bash
git add backend/app/agents/data_agent.py backend/tests/agents/test_data_agent.py
git commit -m "feat: add Data Agent node for EODHD data collection"
```

---

## Task 4: News Agent 노드

**Files:**
- Create: `backend/app/agents/news_agent.py`
- Create: `backend/tests/agents/test_news_agent.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# backend/tests/agents/test_news_agent.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


MOCK_ARTICLES = {
    "politics": [{"title": "News 1", "url": "http://1", "source": {"name": "R"}, "publishedAt": "2026-04-05T08:00:00Z", "description": "desc"}],
    "business": [{"title": "News 2", "url": "http://2", "source": {"name": "C"}, "publishedAt": "2026-04-05T08:00:00Z", "description": "desc"}],
    "society": [{"title": "News 3", "url": "http://3", "source": {"name": "A"}, "publishedAt": "2026-04-05T08:00:00Z", "description": "desc"}],
    "world": [{"title": "News 4", "url": "http://4", "source": {"name": "B"}, "publishedAt": "2026-04-05T08:00:00Z", "description": "desc"}],
}


@pytest.fixture
def mock_newsapi_service():
    service = AsyncMock()
    service.fetch_all_categories.return_value = MOCK_ARTICLES
    return service


@pytest.mark.asyncio
async def test_news_agent_collects_articles(mock_newsapi_service):
    from app.agents.news_agent import news_agent_node
    from app.agents.state import create_initial_state, MarketData

    state = create_initial_state("pre_market")
    state["market_data"] = MarketData()

    with patch("app.agents.news_agent.NewsAPIService", return_value=mock_newsapi_service):
        result = await news_agent_node(state, MagicMock())
        assert result["news_data"] is not None
        assert len(result["news_data"].articles_by_category) == 4
        assert result["news_fallback_used"] is False


@pytest.mark.asyncio
async def test_news_agent_falls_back_to_rss():
    from app.agents.news_agent import news_agent_node
    from app.agents.state import create_initial_state, MarketData

    state = create_initial_state("pre_market")
    state["market_data"] = MarketData()

    mock_newsapi = AsyncMock()
    mock_newsapi.fetch_all_categories.side_effect = Exception("Rate limit")

    mock_rss = MagicMock()
    mock_rss.fetch_news.return_value = [
        {"title": "RSS News", "url": "http://rss1", "source": "Reuters", "published": "2026-04-05"},
    ]

    with patch("app.agents.news_agent.NewsAPIService", return_value=mock_newsapi), \
         patch("app.agents.news_agent.RSSFallbackService", return_value=mock_rss):
        result = await news_agent_node(state, MagicMock())
        assert result["news_fallback_used"] is True
        assert result["news_data"] is not None
```

- [ ] **Step 2: 테스트 실패 확인**

- [ ] **Step 3: news_agent.py 구현**

```python
# backend/app/agents/news_agent.py
import logging
from typing import Any

from app.agents.state import MarketAnalysisState, NewsData
from app.services.newsapi import NewsAPIService
from app.services.rss_fallback import RSSFallbackService
from app.config import Settings

logger = logging.getLogger(__name__)


async def news_agent_node(
    state: MarketAnalysisState,
    config: Any,
) -> dict:
    """LangGraph node: collect news from NewsAPI or RSS fallback."""
    logger.info("News Agent: collecting news (batch=%s)", state["batch_type"])

    settings = config.get("configurable", {}).get("settings") if isinstance(config, dict) else None
    if settings is None:
        settings = Settings()

    fallback_used = False
    articles_by_category: dict[str, list[dict]] = {}

    # Try NewsAPI first (Fast Track)
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
            # Distribute RSS articles evenly across categories
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

    news_data = NewsData(
        articles_by_category=articles_by_category,
        article_summaries=[],
    )

    return {
        "news_data": news_data,
        "news_fallback_used": fallback_used,
    }
```

- [ ] **Step 4: 테스트 통과 확인 (2 passed)**

- [ ] **Step 5: Commit**

```bash
git add backend/app/agents/news_agent.py backend/tests/agents/test_news_agent.py
git commit -m "feat: add News Agent node with RSS fallback"
```

---

## Task 5: Analyst Agent 노드

**Files:**
- Create: `backend/app/agents/analyst_agent.py`
- Create: `backend/tests/agents/test_analyst_agent.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# backend/tests/agents/test_analyst_agent.py
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch


MOCK_CLAUDE_REGIME_RESPONSE = json.dumps({
    "regime": "goldilocks",
    "growth_direction": "high",
    "inflation_direction": "low",
    "regime_probabilities": {
        "goldilocks": 0.60, "reflation": 0.25, "stagflation": 0.10, "deflation": 0.05
    },
    "reasoning": "Strong GDP growth with controlled inflation"
})

MOCK_CLAUDE_SCORING_RESPONSE = json.dumps({
    "scoreboards": [
        {
            "sector_name": "Technology", "etf_symbol": "XLK",
            "base_score": "0.6", "override_score": "0.1",
            "news_sentiment_score": "0.3", "momentum_score": "0.2",
            "final_score": "0.72", "rank": 1,
            "recommendation": "overweight",
            "reasoning": "Goldilocks favors tech"
        }
    ],
    "rotation_signals": [
        {
            "signal_type": "rotation_in", "to_sector": "Technology",
            "strength": "0.8", "final_score": "0.72",
            "reasoning": "Money flowing into tech"
        }
    ],
    "report_summary": "Market in Goldilocks regime. Tech leads.",
    "key_highlights": ["Strong GDP", "Low inflation", "Tech sector outperforming"]
})


@pytest.fixture
def mock_anthropic_client():
    client = MagicMock()
    return client


@pytest.fixture
def mock_supabase_service():
    service = MagicMock()
    service.get_sector_mapping.return_value = [
        {
            "sector_name": "Technology",
            "etf_symbols": ["XLK"],
            "favorable_regimes": ["goldilocks"],
            "unfavorable_regimes": ["stagflation"],
            "override_rules": None,
            "display_order": 3,
        }
    ]
    return service


@pytest.mark.asyncio
async def test_analyst_agent_produces_regime(mock_anthropic_client, mock_supabase_service):
    from app.agents.analyst_agent import analyst_agent_node
    from app.agents.state import create_initial_state, MarketData, NewsData

    state = create_initial_state("pre_market")
    state["market_data"] = MarketData(
        indices=[{"symbol": "SPY", "close": 5200, "change_p": 0.5}],
        sectors=[{"symbol": "XLK", "name": "Technology", "close": 210, "change_p": 1.2, "volume": 50000000}],
        momentum={"XLK": {"momentum_1w": 2.1, "momentum_1m": 5.3, "momentum_3m": 12.0, "momentum_6m": 18.5}},
    )
    state["news_data"] = NewsData(
        articles_by_category={"business": [{"title": "GDP Growth Strong", "description": "Economy growing"}]},
    )

    # Mock Claude API responses
    regime_msg = MagicMock()
    regime_msg.content = [MagicMock(text=MOCK_CLAUDE_REGIME_RESPONSE)]
    scoring_msg = MagicMock()
    scoring_msg.content = [MagicMock(text=MOCK_CLAUDE_SCORING_RESPONSE)]
    mock_anthropic_client.messages.create = MagicMock(side_effect=[regime_msg, scoring_msg])

    with patch("app.agents.analyst_agent.anthropic.Anthropic", return_value=mock_anthropic_client), \
         patch("app.agents.analyst_agent.SupabaseService", return_value=mock_supabase_service):
        result = await analyst_agent_node(state, MagicMock())
        assert result["analysis_results"] is not None
        assert result["analysis_results"].regime is not None
        assert result["analysis_results"].regime["regime"] == "goldilocks"


@pytest.mark.asyncio
async def test_analyst_agent_produces_scoreboards(mock_anthropic_client, mock_supabase_service):
    from app.agents.analyst_agent import analyst_agent_node
    from app.agents.state import create_initial_state, MarketData, NewsData

    state = create_initial_state("pre_market")
    state["market_data"] = MarketData(
        indices=[{"symbol": "SPY", "close": 5200, "change_p": 0.5}],
        sectors=[{"symbol": "XLK", "name": "Technology", "close": 210, "change_p": 1.2, "volume": 50000000}],
        momentum={"XLK": {"momentum_1w": 2.1, "momentum_1m": 5.3, "momentum_3m": 12.0, "momentum_6m": 18.5}},
    )
    state["news_data"] = NewsData(
        articles_by_category={"business": [{"title": "GDP Strong", "description": "Growing"}]},
    )

    regime_msg = MagicMock()
    regime_msg.content = [MagicMock(text=MOCK_CLAUDE_REGIME_RESPONSE)]
    scoring_msg = MagicMock()
    scoring_msg.content = [MagicMock(text=MOCK_CLAUDE_SCORING_RESPONSE)]
    mock_anthropic_client.messages.create = MagicMock(side_effect=[regime_msg, scoring_msg])

    with patch("app.agents.analyst_agent.anthropic.Anthropic", return_value=mock_anthropic_client), \
         patch("app.agents.analyst_agent.SupabaseService", return_value=mock_supabase_service):
        result = await analyst_agent_node(state, MagicMock())
        assert len(result["analysis_results"].scoreboards) > 0
        assert result["analysis_results"].report is not None
```

- [ ] **Step 2: 테스트 실패 확인**

- [ ] **Step 3: analyst_agent.py 구현**

```python
# backend/app/agents/analyst_agent.py
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anthropic

from app.agents.state import MarketAnalysisState, AnalysisResults
from app.config import Settings
from app.services.supabase import SupabaseService

logger = logging.getLogger(__name__)

STRATEGY_DOC_PATH = Path(__file__).parent.parent.parent.parent / "docs" / "sector-rotation-strategy.md"

REGIME_DETECTION_PROMPT = """You are a macro-economic analyst. Based on the market data and news below, determine the current macro regime.

## Macro Regime Matrix (2D)
- **Goldilocks**: High Growth + Low Inflation — bull market, risk-on
- **Reflation**: High Growth + High Inflation — overheating, commodity demand
- **Stagflation**: Low Growth + High Inflation — cost push, worst market
- **Deflation**: Low Growth + Low Inflation — recession, safe haven

## Market Data
{market_data}

## News Summary
{news_summary}

## Sector Regime Mapping
{sector_mapping}

Respond with ONLY valid JSON (no markdown, no explanation):
{{
    "regime": "goldilocks|reflation|stagflation|deflation",
    "growth_direction": "high|low",
    "inflation_direction": "high|low",
    "regime_probabilities": {{"goldilocks": 0.0, "reflation": 0.0, "stagflation": 0.0, "deflation": 0.0}},
    "reasoning": "explanation in Korean"
}}"""

SCORING_PROMPT = """You are a sector rotation analyst. Given the detected macro regime and market context, score each sector.

## Current Regime
{regime_json}

## Sector Mapping with Override Rules
{sector_mapping}

## Market Momentum Data
{momentum_data}

## News by Category
{news_data}

## Scoring Formula
Final Score = (Base Score x Regime Confidence) + Override Adjustment + (News Sentiment x 0.2) + (Momentum x 0.15)
- Base Score: favorable regime = +0.6, unfavorable = -0.4, neutral = 0.0
- Override: check override_rules triggers against news, apply if matched (-0.5 ~ +0.5)
- Recommendation: >= +0.5 overweight, -0.2 ~ +0.5 neutral, < -0.2 underweight

Respond with ONLY valid JSON (no markdown):
{{
    "scoreboards": [
        {{
            "sector_name": "...", "etf_symbol": "...",
            "base_score": "0.0", "override_score": "0.0",
            "news_sentiment_score": "0.0", "momentum_score": "0.0",
            "final_score": "0.0", "rank": 1,
            "recommendation": "overweight|neutral|underweight",
            "reasoning": "explanation in Korean"
        }}
    ],
    "rotation_signals": [
        {{
            "signal_type": "rotation_in|rotation_out|regime_shift",
            "from_sector": "...|null", "to_sector": "...|null",
            "strength": "0.0", "final_score": "0.0",
            "reasoning": "explanation in Korean"
        }}
    ],
    "report_summary": "overall market summary in Korean",
    "key_highlights": ["point 1", "point 2", "point 3"]
}}"""


async def analyst_agent_node(
    state: MarketAnalysisState,
    config: Any,
) -> dict:
    """LangGraph node: analyze market data + news using Claude API."""
    logger.info("Analyst Agent: starting analysis (batch=%s)", state["batch_type"])

    settings = config.get("configurable", {}).get("settings") if isinstance(config, dict) else None
    if settings is None:
        settings = Settings()

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Load sector mapping from Supabase
    try:
        supa = SupabaseService(settings)
        sector_mapping = supa.get_sector_mapping()
    except Exception as e:
        logger.warning("Failed to load sector mapping from Supabase: %s. Using empty.", e)
        sector_mapping = []

    market_data = state.get("market_data")
    news_data = state.get("news_data")
    batch_type = state["batch_type"]
    now = datetime.now(timezone.utc)

    # Format data for prompts
    market_summary = json.dumps({
        "indices": market_data.indices if market_data else [],
        "sectors": market_data.sectors if market_data else [],
    }, default=str, ensure_ascii=False)

    news_summary = ""
    if news_data:
        for cat, articles in news_data.articles_by_category.items():
            news_summary += f"\n### {cat}\n"
            for a in articles[:3]:
                title = a.get("title", "")
                desc = a.get("description", "")
                news_summary += f"- {title}: {desc}\n"

    mapping_str = json.dumps(sector_mapping, default=str, ensure_ascii=False)
    momentum_str = json.dumps(market_data.momentum if market_data else {}, default=str)

    # Step 1: Macro Regime Detection
    regime_prompt = REGIME_DETECTION_PROMPT.format(
        market_data=market_summary,
        news_summary=news_summary,
        sector_mapping=mapping_str,
    )

    try:
        regime_response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": regime_prompt}],
        )
        regime_text = regime_response.content[0].text
        regime_data = json.loads(regime_text)
    except Exception as e:
        logger.error("Regime detection failed: %s", e)
        regime_data = {
            "regime": "goldilocks",
            "growth_direction": "high",
            "inflation_direction": "low",
            "regime_probabilities": {"goldilocks": 0.25, "reflation": 0.25, "stagflation": 0.25, "deflation": 0.25},
            "reasoning": "분석 실패 - 기본값 사용",
        }

    regime_data["batch_type"] = batch_type
    regime_data["analyzed_at"] = now.isoformat()

    # Steps 2-4: Scoring & Reporting
    scoring_prompt = SCORING_PROMPT.format(
        regime_json=json.dumps(regime_data, ensure_ascii=False),
        sector_mapping=mapping_str,
        momentum_data=momentum_str,
        news_data=news_summary,
    )

    try:
        scoring_response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[{"role": "user", "content": scoring_prompt}],
        )
        scoring_text = scoring_response.content[0].text
        scoring_data = json.loads(scoring_text)
    except Exception as e:
        logger.error("Scoring failed: %s", e)
        scoring_data = {
            "scoreboards": [],
            "rotation_signals": [],
            "report_summary": "분석 실패",
            "key_highlights": [],
        }

    # Add metadata to scoreboards
    for sb in scoring_data.get("scoreboards", []):
        sb["batch_type"] = batch_type
        sb["scored_at"] = now.isoformat()

    for sig in scoring_data.get("rotation_signals", []):
        sig["batch_type"] = batch_type
        sig["detected_at"] = now.isoformat()

    # Build report
    report = {
        "batch_type": batch_type,
        "summary": scoring_data.get("report_summary", ""),
        "key_highlights": scoring_data.get("key_highlights", []),
        "report_date": now.strftime("%Y-%m-%d"),
        "analyzed_at": now.isoformat(),
        "disclaimer": "본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다.",
    }

    analysis_results = AnalysisResults(
        regime=regime_data,
        scoreboards=scoring_data.get("scoreboards", []),
        rotation_signals=scoring_data.get("rotation_signals", []),
        news_impacts=[],
        report=report,
    )

    logger.info("Analyst Agent: analysis complete. Regime=%s", regime_data.get("regime"))
    return {"analysis_results": analysis_results}
```

- [ ] **Step 4: 테스트 통과 확인 (2 passed)**

- [ ] **Step 5: Commit**

```bash
git add backend/app/agents/analyst_agent.py backend/tests/agents/test_analyst_agent.py
git commit -m "feat: add Analyst Agent with 4-step sector rotation analysis"
```

---

## Task 6: LangGraph 메인 그래프

**Files:**
- Create: `backend/app/agents/graph.py`
- Create: `backend/tests/agents/test_graph.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# backend/tests/agents/test_graph.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.state import MarketData, NewsData, AnalysisResults


@pytest.mark.asyncio
async def test_graph_builds_without_error():
    from app.agents.graph import build_graph
    graph = build_graph()
    assert graph is not None


@pytest.mark.asyncio
async def test_graph_has_correct_nodes():
    from app.agents.graph import build_graph
    graph = build_graph()
    # LangGraph compiled graph has nodes attribute
    node_names = list(graph.nodes.keys())
    assert "data_agent" in node_names
    assert "news_agent" in node_names
    assert "analyst_agent" in node_names
```

- [ ] **Step 2: 테스트 실패 확인**

- [ ] **Step 3: graph.py 구현**

```python
# backend/app/agents/graph.py
from langgraph.graph import StateGraph, END

from app.agents.state import MarketAnalysisState
from app.agents.data_agent import data_agent_node
from app.agents.news_agent import news_agent_node
from app.agents.analyst_agent import analyst_agent_node


def build_graph() -> StateGraph:
    """Build the LangGraph pipeline: Data Agent → News Agent → Analyst Agent."""
    graph = StateGraph(MarketAnalysisState)

    graph.add_node("data_agent", data_agent_node)
    graph.add_node("news_agent", news_agent_node)
    graph.add_node("analyst_agent", analyst_agent_node)

    graph.set_entry_point("data_agent")
    graph.add_edge("data_agent", "news_agent")
    graph.add_edge("news_agent", "analyst_agent")
    graph.add_edge("analyst_agent", END)

    return graph.compile()
```

- [ ] **Step 4: 테스트 통과 확인 (2 passed)**

- [ ] **Step 5: Commit**

```bash
git add backend/app/agents/graph.py backend/tests/agents/test_graph.py
git commit -m "feat: add LangGraph pipeline graph (data → news → analyst)"
```

---

## Task 7: NewsAPI MCP 서버

**Files:**
- Create: `backend/app/mcp/news_server.py`

- [ ] **Step 1: news_server.py 구현**

```python
# backend/app/mcp/news_server.py
"""NewsAPI MCP Server - wraps NewsAPI.org for use as an agent tool."""
import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("newsapi")

NEWSAPI_BASE_URL = "https://newsapi.org/v2"


def _get_api_key() -> str:
    key = os.environ.get("NEWSAPI_KEY", "")
    if not key:
        raise ValueError("NEWSAPI_KEY environment variable is not set")
    return key


@mcp.tool()
async def get_top_headlines(
    category: str = "business",
    country: str = "us",
    page_size: int = 5,
) -> str:
    """Fetch top news headlines by category from NewsAPI.

    Args:
        category: News category (business, technology, science, general, health, sports, entertainment)
        country: Country code (default: us)
        page_size: Number of results (default: 5, max: 100)
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            f"{NEWSAPI_BASE_URL}/top-headlines",
            params={
                "apiKey": _get_api_key(),
                "category": category,
                "country": country,
                "pageSize": page_size,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    articles = data.get("articles", [])
    results = []
    for a in articles:
        results.append({
            "title": a.get("title", ""),
            "source": a.get("source", {}).get("name", ""),
            "url": a.get("url", ""),
            "publishedAt": a.get("publishedAt", ""),
            "description": a.get("description", ""),
        })

    return json.dumps(results, ensure_ascii=False)


@mcp.tool()
async def search_news(
    query: str,
    from_date: str = "",
    to_date: str = "",
    page_size: int = 5,
) -> str:
    """Search news articles by keyword.

    Args:
        query: Search keyword
        from_date: Start date (YYYY-MM-DD format, optional)
        to_date: End date (YYYY-MM-DD format, optional)
        page_size: Number of results (default: 5)
    """
    params = {
        "apiKey": _get_api_key(),
        "q": query,
        "pageSize": page_size,
        "language": "en",
    }
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f"{NEWSAPI_BASE_URL}/everything", params=params)
        resp.raise_for_status()
        data = resp.json()

    articles = data.get("articles", [])
    results = []
    for a in articles:
        results.append({
            "title": a.get("title", ""),
            "source": a.get("source", {}).get("name", ""),
            "url": a.get("url", ""),
            "publishedAt": a.get("publishedAt", ""),
            "description": a.get("description", ""),
        })

    return json.dumps(results, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
```

- [ ] **Step 2: .mcp.json 업데이트 (프로젝트 루트)**

newsapi 서버 추가:
```json
{
  "mcpServers": {
    "fetch": {
      "command": "npx",
      "args": ["@anthropic-ai/fetch-mcp"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@anthropic-ai/playwright-mcp"]
    },
    "newsapi": {
      "command": "python",
      "args": ["-m", "app.mcp.news_server"],
      "cwd": "./backend"
    }
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/mcp/news_server.py .mcp.json
git commit -m "feat: add NewsAPI MCP server with headline and search tools"
```

---

## Task 8: 전체 통합 테스트 + 정리

- [ ] **Step 1: 전체 테스트 실행**

```bash
cd backend && .venv/Scripts/python -m pytest -v --tb=short
```
Expected: All tests pass (~30+ tests)

- [ ] **Step 2: ruff 린트 실행**

```bash
cd backend && .venv/Scripts/ruff check app/ tests/ --fix
```

- [ ] **Step 3: 수정사항 있으면 커밋**

```bash
git add -A && git commit -m "fix: lint cleanup for Phase 2"
```

---

## Phase 2 완료 기준

- `app/agents/state.py` — 공유 상태 스키마
- `app/agents/data_agent.py` — EODHD 데이터 수집 노드
- `app/agents/news_agent.py` — 뉴스 수집 + RSS fallback 노드
- `app/agents/analyst_agent.py` — Claude 4단계 분석 노드
- `app/agents/graph.py` — LangGraph 파이프라인 (data→news→analyst)
- `app/mcp/news_server.py` — NewsAPI MCP 서버
- 전체 테스트 ~30개 통과

## 다음 Phase

Phase 2 완료 후 → **Phase 3: API + Scheduler** (FastAPI 엔드포인트 + APScheduler 배치)
