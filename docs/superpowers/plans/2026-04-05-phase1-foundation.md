# Phase 1: Foundation — 프로젝트 기반 구축

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Backend(FastAPI + Python) 스캐폴딩, Supabase 테이블 생성, 외부 API 클라이언트(EODHD, NewsAPI, RSS) 구현 — 에이전트 파이프라인 구축(Phase 2)의 기반

**Architecture:** FastAPI 앱 + pydantic-settings 환경 관리 + httpx 비동기 HTTP 클라이언트 + Supabase Python SDK. 각 외부 서비스는 `services/` 하위에 독립 클라이언트로 격리.

**Tech Stack:** Python 3.12, FastAPI, uvicorn, httpx, pydantic v2, pydantic-settings, supabase-py, feedparser, pytest, pytest-asyncio, ruff

**Spec:** `docs/superpowers/specs/2026-04-05-market-insights-dashboard-design.md`
**Sector Strategy:** `docs/sector-rotation-strategy.md`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `backend/pyproject.toml` | 프로젝트 메타 + 의존성 |
| Create | `backend/.env.example` | 환경변수 템플릿 |
| Create | `backend/.gitignore` | Python/env 무시 패턴 |
| Create | `backend/app/__init__.py` | 패키지 초기화 |
| Create | `backend/app/main.py` | FastAPI 앱 진입점 |
| Create | `backend/app/config.py` | pydantic-settings 환경 관리 |
| Create | `backend/app/models/__init__.py` | 모델 패키지 |
| Create | `backend/app/models/market.py` | 지수/섹터 pydantic 스키마 |
| Create | `backend/app/models/news.py` | 뉴스 pydantic 스키마 |
| Create | `backend/app/models/analysis.py` | 분석결과 pydantic 스키마 (macro_regimes, scoreboards 등) |
| Create | `backend/app/services/__init__.py` | 서비스 패키지 |
| Create | `backend/app/services/supabase.py` | Supabase 클라이언트 |
| Create | `backend/app/services/eodhd.py` | EODHD API 클라이언트 |
| Create | `backend/app/services/newsapi.py` | NewsAPI 클라이언트 |
| Create | `backend/app/services/rss_fallback.py` | Google News RSS 폴백 |
| Create | `backend/app/api/__init__.py` | API 패키지 |
| Create | `backend/app/api/deps.py` | 공통 의존성 (settings, supabase) |
| Create | `backend/app/api/routes/__init__.py` | 라우트 패키지 |
| Create | `backend/app/api/routes/health.py` | 헬스체크 엔드포인트 |
| Create | `backend/tests/__init__.py` | 테스트 패키지 |
| Create | `backend/tests/conftest.py` | pytest 공통 fixtures |
| Create | `backend/tests/test_config.py` | config 테스트 |
| Create | `backend/tests/test_models.py` | 모델 직렬화 테스트 |
| Create | `backend/tests/services/__init__.py` | 서비스 테스트 패키지 |
| Create | `backend/tests/services/test_eodhd.py` | EODHD 클라이언트 테스트 |
| Create | `backend/tests/services/test_newsapi.py` | NewsAPI 클라이언트 테스트 |
| Create | `backend/tests/services/test_rss_fallback.py` | RSS 폴백 테스트 |
| Create | `backend/tests/services/test_supabase.py` | Supabase 클라이언트 테스트 |
| Create | `backend/tests/api/test_health.py` | 헬스체크 API 테스트 |
| Create | `backend/supabase/migrations/001_initial_schema.sql` | Supabase DDL |
| Create | `.mcp.json` | MCP 서버 등록 (프로젝트 루트) |

---

## Task 1: 프로젝트 스캐폴딩 + 의존성 설정

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/.env.example`
- Create: `backend/.gitignore`
- Create: `backend/app/__init__.py`

- [ ] **Step 1: backend 디렉토리 구조 생성**

```bash
mkdir -p backend/app/{api/routes,agents,mcp,models,services,scheduler}
mkdir -p backend/tests/{api,services}
mkdir -p backend/supabase/migrations
```

- [ ] **Step 2: pyproject.toml 작성**

```toml
[project]
name = "economi-analyzer-backend"
version = "0.1.0"
description = "AI-Driven Market Insights Dashboard - Sector Rotation Analysis"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    "supabase>=2.0.0",
    "feedparser>=6.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.6.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
```

- [ ] **Step 3: .env.example 작성**

```env
# Claude API
ANTHROPIC_API_KEY=sk-ant-xxxxx

# EODHD Financial Data
EODHD_API_KEY=xxxxxxxx

# NewsAPI.org
NEWSAPI_KEY=xxxxxxxx

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJxxxxx
```

- [ ] **Step 4: .gitignore 작성**

```gitignore
__pycache__/
*.py[cod]
.venv/
.env
*.egg-info/
dist/
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
```

- [ ] **Step 5: __init__.py 파일 생성**

모든 패키지 디렉토리에 빈 `__init__.py` 생성:
```bash
touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/routes/__init__.py
touch backend/app/agents/__init__.py
touch backend/app/mcp/__init__.py
touch backend/app/models/__init__.py
touch backend/app/services/__init__.py
touch backend/app/scheduler/__init__.py
touch backend/tests/__init__.py
touch backend/tests/api/__init__.py
touch backend/tests/services/__init__.py
```

- [ ] **Step 6: 가상환경 생성 + 의존성 설치**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run: `pip list | grep fastapi`
Expected: `fastapi` 버전 출력

- [ ] **Step 7: Commit**

```bash
git init
git add backend/pyproject.toml backend/.env.example backend/.gitignore
git add backend/app/__init__.py backend/app/api/__init__.py backend/app/api/routes/__init__.py
git add backend/app/agents/__init__.py backend/app/mcp/__init__.py
git add backend/app/models/__init__.py backend/app/services/__init__.py
git add backend/app/scheduler/__init__.py
git add backend/tests/__init__.py backend/tests/api/__init__.py backend/tests/services/__init__.py
git commit -m "chore: scaffold backend project with dependencies"
```

---

## Task 2: 환경 설정 (Config)

**Files:**
- Create: `backend/app/config.py`
- Create: `backend/tests/test_config.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# backend/tests/test_config.py
import os
import pytest


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("EODHD_API_KEY", "test-eodhd")
    monkeypatch.setenv("NEWSAPI_KEY", "test-news")
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")

    from app.config import Settings
    settings = Settings()

    assert settings.anthropic_api_key == "test-key"
    assert settings.eodhd_api_key == "test-eodhd"
    assert settings.newsapi_key == "test-news"
    assert settings.supabase_url == "https://test.supabase.co"
    assert settings.supabase_service_key == "test-service-key"


def test_settings_has_defaults():
    """batch_schedule과 같은 설정에 기본값이 존재하는지 확인."""
    from app.config import Settings
    settings = Settings(
        anthropic_api_key="x",
        eodhd_api_key="x",
        newsapi_key="x",
        supabase_url="https://x.supabase.co",
        supabase_service_key="x",
    )
    assert settings.pre_market_time == "08:30"
    assert settings.post_market_time == "17:00"
    assert settings.timezone == "US/Eastern"
```

- [ ] **Step 2: 테스트가 실패하는지 확인**

Run: `cd backend && python -m pytest tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.config'`

- [ ] **Step 3: config.py 구현**

```python
# backend/app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    anthropic_api_key: str
    eodhd_api_key: str
    newsapi_key: str

    # Supabase
    supabase_url: str
    supabase_service_key: str

    # Scheduler
    pre_market_time: str = "08:30"
    post_market_time: str = "17:00"
    timezone: str = "US/Eastern"

    # NewsAPI
    newsapi_daily_limit: int = 100
    newsapi_categories: list[str] = ["business", "technology", "science", "general"]

    # EODHD
    eodhd_base_url: str = "https://eodhd.com/api"

    # Playwright
    playwright_timeout_sec: int = 30
    playwright_max_instances: int = 2

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd backend && python -m pytest tests/test_config.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/config.py backend/tests/test_config.py
git commit -m "feat: add pydantic-settings config with env management"
```

---

## Task 3: Pydantic 모델 (Market / News / Analysis)

**Files:**
- Create: `backend/app/models/market.py`
- Create: `backend/app/models/news.py`
- Create: `backend/app/models/analysis.py`
- Create: `backend/tests/test_models.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# backend/tests/test_models.py
from datetime import datetime, timezone
from decimal import Decimal


def test_market_index_model():
    from app.models.market import MarketIndex
    idx = MarketIndex(
        symbol="SPY",
        name="S&P 500",
        price=Decimal("5200.50"),
        change_percent=Decimal("0.55"),
        collected_at=datetime.now(timezone.utc),
    )
    assert idx.symbol == "SPY"
    assert idx.price == Decimal("5200.50")


def test_sector_model_with_momentum():
    from app.models.market import Sector
    sector = Sector(
        name="Technology",
        etf_symbol="XLK",
        price=Decimal("210.30"),
        change_percent=Decimal("1.2"),
        volume=50_000_000,
        avg_volume_20d=45_000_000,
        volume_change_percent=Decimal("11.1"),
        relative_strength=Decimal("1.05"),
        momentum_1w=Decimal("2.1"),
        momentum_1m=Decimal("5.3"),
        momentum_3m=Decimal("12.0"),
        momentum_6m=Decimal("18.5"),
        rs_rank=1,
        collected_at=datetime.now(timezone.utc),
    )
    assert sector.etf_symbol == "XLK"
    assert sector.rs_rank == 1


def test_economic_indicator_model():
    from app.models.market import EconomicIndicator
    ind = EconomicIndicator(
        indicator_name="fed_rate",
        value=Decimal("5.25"),
        previous_value=Decimal("5.00"),
        change_direction="rising",
        source="EODHD",
        reported_at=datetime.now(timezone.utc),
    )
    assert ind.change_direction == "rising"


def test_news_article_model():
    from app.models.news import NewsArticle
    article = NewsArticle(
        category="business",
        title="Fed Holds Rates Steady",
        source="Reuters",
        url="https://reuters.com/article/1",
        summary="The Federal Reserve held rates...",
        published_at=datetime.now(timezone.utc),
        collected_at=datetime.now(timezone.utc),
    )
    assert article.category == "business"


def test_macro_regime_model():
    from app.models.analysis import MacroRegime
    regime = MacroRegime(
        regime="goldilocks",
        growth_direction="high",
        inflation_direction="low",
        regime_probabilities={
            "goldilocks": 0.60,
            "reflation": 0.25,
            "stagflation": 0.10,
            "deflation": 0.05,
        },
        reasoning="Strong GDP growth with falling CPI",
        batch_type="pre_market",
        analyzed_at=datetime.now(timezone.utc),
    )
    assert regime.regime == "goldilocks"
    assert regime.regime_probabilities["goldilocks"] == 0.60


def test_sector_scoreboard_model():
    from app.models.analysis import SectorScoreboard
    sb = SectorScoreboard(
        sector_name="Technology",
        etf_symbol="XLK",
        base_score=Decimal("0.6"),
        override_score=Decimal("0.1"),
        news_sentiment_score=Decimal("0.3"),
        momentum_score=Decimal("0.2"),
        final_score=Decimal("0.72"),
        rank=1,
        recommendation="overweight",
        reasoning="Goldilocks regime favors tech",
        batch_type="pre_market",
        scored_at=datetime.now(timezone.utc),
    )
    assert sb.recommendation == "overweight"
    assert sb.rank == 1


def test_rotation_signal_model():
    from app.models.analysis import RotationSignal
    sig = RotationSignal(
        signal_type="rotation_in",
        to_sector="Technology",
        strength=Decimal("0.8"),
        final_score=Decimal("0.72"),
        reasoning="Money flowing into tech sector",
        batch_type="pre_market",
        detected_at=datetime.now(timezone.utc),
    )
    assert sig.signal_type == "rotation_in"
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd backend && python -m pytest tests/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: market.py 모델 구현**

```python
# backend/app/models/market.py
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class MarketIndex(BaseModel):
    symbol: str
    name: str
    price: Decimal
    change_percent: Decimal
    collected_at: datetime


class Sector(BaseModel):
    name: str
    etf_symbol: str
    price: Decimal
    change_percent: Decimal
    volume: int
    avg_volume_20d: int | None = None
    volume_change_percent: Decimal | None = None
    relative_strength: Decimal | None = None
    momentum_1w: Decimal | None = None
    momentum_1m: Decimal | None = None
    momentum_3m: Decimal | None = None
    momentum_6m: Decimal | None = None
    rs_rank: int | None = None
    collected_at: datetime


class EconomicIndicator(BaseModel):
    indicator_name: str
    value: Decimal
    previous_value: Decimal | None = None
    change_direction: str  # rising, falling, stable
    source: str
    reported_at: datetime
```

- [ ] **Step 4: news.py 모델 구현**

```python
# backend/app/models/news.py
from datetime import datetime

from pydantic import BaseModel


class NewsArticle(BaseModel):
    category: str  # business, technology, science, general
    title: str
    source: str
    url: str
    summary: str | None = None
    published_at: datetime
    collected_at: datetime


class NewsImpactAnalysis(BaseModel):
    news_url: str
    sector_name: str
    impact_score: float  # -1.0 ~ +1.0
    impact_direction: str  # bullish, bearish, neutral
    reasoning: str
    rotation_relevance: float = 0.0  # 0 ~ 1.0
    batch_type: str
    analyzed_at: datetime
```

- [ ] **Step 5: analysis.py 모델 구현**

```python
# backend/app/models/analysis.py
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class MacroRegime(BaseModel):
    regime: str  # goldilocks, reflation, stagflation, deflation
    growth_direction: str  # high, low
    inflation_direction: str  # high, low
    transition_from: str | None = None
    transition_probability: float | None = None
    regime_probabilities: dict[str, float]
    indicators_snapshot: dict | None = None
    reasoning: str
    batch_type: str
    analyzed_at: datetime


class SectorScoreboard(BaseModel):
    sector_name: str
    etf_symbol: str
    base_score: Decimal
    override_score: Decimal
    news_sentiment_score: Decimal
    momentum_score: Decimal
    final_score: Decimal
    rank: int
    recommendation: str  # overweight, neutral, underweight
    reasoning: str
    batch_type: str
    scored_at: datetime


class RotationSignal(BaseModel):
    signal_type: str  # rotation_in, rotation_out, regime_shift, override_triggered
    from_sector: str | None = None
    to_sector: str | None = None
    strength: Decimal
    base_score: Decimal | None = None
    override_adjustment: Decimal | None = None
    final_score: Decimal
    reasoning: str
    supporting_news_urls: list[str] = []
    batch_type: str
    detected_at: datetime


class MarketReport(BaseModel):
    batch_type: str
    summary: str
    key_highlights: list[str]
    regime: MacroRegime
    top_sectors: list[SectorScoreboard]
    bottom_sectors: list[SectorScoreboard]
    rotation_signals: list[RotationSignal]
    report_date: str  # YYYY-MM-DD
    analyzed_at: datetime
    disclaimer: str = "본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다."
```

- [ ] **Step 6: 테스트 통과 확인**

Run: `cd backend && python -m pytest tests/test_models.py -v`
Expected: 7 passed

- [ ] **Step 7: Commit**

```bash
git add backend/app/models/ backend/tests/test_models.py
git commit -m "feat: add pydantic models for market, news, and analysis"
```

---

## Task 4: Supabase 마이그레이션 + 클라이언트

**Files:**
- Create: `backend/supabase/migrations/001_initial_schema.sql`
- Create: `backend/app/services/supabase.py`
- Create: `backend/tests/services/test_supabase.py`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: SQL 마이그레이션 작성**

```sql
-- backend/supabase/migrations/001_initial_schema.sql

-- 주요 지수
CREATE TABLE IF NOT EXISTS market_indices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    name TEXT NOT NULL,
    price DECIMAL NOT NULL,
    change_percent DECIMAL NOT NULL,
    collected_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 섹터 데이터
CREATE TABLE IF NOT EXISTS sectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    etf_symbol TEXT NOT NULL,
    price DECIMAL NOT NULL,
    change_percent DECIMAL NOT NULL,
    volume BIGINT NOT NULL,
    avg_volume_20d BIGINT,
    volume_change_percent DECIMAL,
    relative_strength DECIMAL,
    momentum_1w DECIMAL,
    momentum_1m DECIMAL,
    momentum_3m DECIMAL,
    momentum_6m DECIMAL,
    rs_rank INTEGER,
    collected_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 경제 지표
CREATE TABLE IF NOT EXISTS economic_indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_name TEXT NOT NULL,
    value DECIMAL NOT NULL,
    previous_value DECIMAL,
    change_direction TEXT NOT NULL,
    source TEXT NOT NULL,
    reported_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 거시 경제 국면
CREATE TABLE IF NOT EXISTS macro_regimes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    regime TEXT NOT NULL,
    growth_direction TEXT NOT NULL,
    inflation_direction TEXT NOT NULL,
    transition_from TEXT,
    transition_probability DECIMAL,
    regime_probabilities JSONB NOT NULL,
    indicators_snapshot JSONB,
    reasoning TEXT NOT NULL,
    batch_type TEXT NOT NULL,
    analyzed_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 섹터-국면 매핑 (참조 테이블)
CREATE TABLE IF NOT EXISTS sector_regime_mapping (
    id SERIAL PRIMARY KEY,
    sector_name TEXT NOT NULL,
    sub_classification TEXT,
    etf_symbols TEXT[] NOT NULL,
    favorable_regimes TEXT[] NOT NULL,
    unfavorable_regimes TEXT[] NOT NULL,
    override_rules JSONB,
    sensitivity_factors TEXT[],
    analysis_note TEXT,
    display_order INTEGER NOT NULL
);

-- 뉴스
CREATE TABLE IF NOT EXISTS news_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    summary TEXT,
    published_at TIMESTAMPTZ NOT NULL,
    collected_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 뉴스 영향 분석
CREATE TABLE IF NOT EXISTS news_impact_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    news_id UUID REFERENCES news_articles(id),
    sector_name TEXT NOT NULL,
    impact_score DECIMAL NOT NULL,
    impact_direction TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    rotation_relevance DECIMAL DEFAULT 0,
    batch_type TEXT NOT NULL,
    analyzed_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 순환매 신호
CREATE TABLE IF NOT EXISTS rotation_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    regime_id UUID REFERENCES macro_regimes(id),
    signal_type TEXT NOT NULL,
    from_sector TEXT,
    to_sector TEXT,
    strength DECIMAL NOT NULL,
    base_score DECIMAL,
    override_adjustment DECIMAL,
    final_score DECIMAL NOT NULL,
    reasoning TEXT NOT NULL,
    supporting_news UUID[],
    batch_type TEXT NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 섹터 스코어보드
CREATE TABLE IF NOT EXISTS sector_scoreboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    regime_id UUID REFERENCES macro_regimes(id),
    sector_name TEXT NOT NULL,
    etf_symbol TEXT NOT NULL,
    base_score DECIMAL NOT NULL,
    override_score DECIMAL NOT NULL,
    news_sentiment_score DECIMAL NOT NULL,
    momentum_score DECIMAL NOT NULL,
    final_score DECIMAL NOT NULL,
    rank INTEGER NOT NULL,
    recommendation TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    batch_type TEXT NOT NULL,
    scored_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 종합 리포트
CREATE TABLE IF NOT EXISTS market_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    key_highlights JSONB NOT NULL,
    report_date DATE NOT NULL,
    analyzed_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 섹터-국면 매핑 초기 데이터
INSERT INTO sector_regime_mapping (sector_name, sub_classification, etf_symbols, favorable_regimes, unfavorable_regimes, override_rules, sensitivity_factors, analysis_note, display_order)
VALUES
('Financials', NULL, '{XLF}', '{reflation}', '{deflation}', '{"trigger":"rate_spread_widening","action":"boost_score","description":"금리 스프레드 확대 시 가중치 부여"}', '{interest_rate,yield_spread}', '금리 인상기에 가중치 부여', 1),
('Real Estate', NULL, '{XLRE}', '{goldilocks}', '{stagflation}', '{"trigger":"rate_cut_news","action":"strong_buy_signal","description":"금리 하락 뉴스 발생 시 강한 매수 시그널"}', '{interest_rate,housing}', '금리 하락 뉴스 → 강한 매수 시그널', 2),
('Technology', NULL, '{XLK}', '{goldilocks}', '{stagflation}', '{"trigger":"real_rate_decline AND high_fcf","condition_regime":"deflation","action":"upgrade_to_defensive","description":"디플레이션이더라도 실질금리 하락 + FCF 우수 시 방어주 인식"}', '{real_rate,fcf}', '디플레이션+실질금리하락+FCF우수 → 방어주 격상', 3),
('Consumer Discretionary', NULL, '{XLY}', '{goldilocks}', '{deflation,stagflation}', NULL, '{employment,consumer_sentiment}', '고용/소비심리 지표 최민감', 4),
('Industrials', NULL, '{XLI}', '{reflation}', '{deflation}', '{"trigger":"infrastructure_spending_news","action":"boost_score","description":"인프라 투자/공급망 뉴스 가중치"}', '{infrastructure,supply_chain}', '인프라 투자 뉴스 가중치', 5),
('Materials', NULL, '{XLB}', '{reflation}', '{deflation}', '{"trigger":"commodity_price_surge","action":"boost_score","description":"원자재 가격 급등 시 가중치"}', '{copper,iron_ore,commodities}', '원자재 가격 연동', 6),
('Energy', NULL, '{XLE}', '{stagflation,reflation}', '{goldilocks,deflation}', '{"trigger":"geopolitical_risk OR inflation_sticky","action":"upgrade_to_top_defensive","description":"지정학 리스크나 인플레 고착화 시 최우선 방어주 격상"}', '{geopolitical,oil_price,inflation}', '지정학 리스크/인플레 고착화 → 최우선 방어주', 7),
('Utilities', NULL, '{XLU}', '{deflation}', '{reflation,goldilocks}', NULL, '{bond_yield,dividend_yield}', '배당수익률 vs 채권금리 비교', 8),
('Healthcare', NULL, '{XLV}', '{deflation}', '{goldilocks,reflation}', NULL, '{drug_approval,regulation}', '강세장에서 상대적 underperform', 9),
('Consumer Staples', NULL, '{XLP}', '{deflation,stagflation}', '{goldilocks,reflation}', '{"trigger":"pricing_power_positive_news","action":"boost_score","description":"가격전가력 관련 긍정 뉴스 시 가중치"}', '{pricing_power,food_prices}', '가격전가력 뉴스 가중치', 10),
('Communication', 'Media/Platform', '{META,GOOGL}', '{goldilocks}', '{stagflation,deflation}', NULL, '{ad_revenue,digital_spending}', '기술주 동일 논리 (메타, 알파벳)', 11),
('Communication', 'Telecom', '{VOX,T,VZ}', '{deflation}', '{goldilocks}', NULL, '{subscriber_growth,dividend_yield}', '유틸리티 동일 논리 (AT&T, 버라이즌)', 12);
```

- [ ] **Step 2: conftest.py 작성 (공통 fixtures)**

```python
# backend/tests/conftest.py
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("EODHD_API_KEY", "test-eodhd")
    monkeypatch.setenv("NEWSAPI_KEY", "test-news")
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_KEY", "test-service-key")

    from app.config import Settings
    return Settings()


@pytest.fixture
def mock_supabase_client():
    client = MagicMock()
    client.table.return_value.insert.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[{"id": "test-uuid"}])
    )
    client.table.return_value.select.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[])
    )
    return client
```

- [ ] **Step 3: 실패하는 Supabase 클라이언트 테스트**

```python
# backend/tests/services/test_supabase.py
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from decimal import Decimal


def test_supabase_client_init(mock_settings):
    from app.services.supabase import SupabaseService
    with patch("app.services.supabase.create_client") as mock_create:
        mock_create.return_value = MagicMock()
        service = SupabaseService(mock_settings)
        mock_create.assert_called_once_with(
            mock_settings.supabase_url,
            mock_settings.supabase_service_key,
        )


def test_insert_market_index(mock_settings, mock_supabase_client):
    from app.services.supabase import SupabaseService
    from app.models.market import MarketIndex

    with patch("app.services.supabase.create_client", return_value=mock_supabase_client):
        service = SupabaseService(mock_settings)
        idx = MarketIndex(
            symbol="SPY",
            name="S&P 500",
            price=Decimal("5200.50"),
            change_percent=Decimal("0.55"),
            collected_at=datetime.now(timezone.utc),
        )
        service.insert_market_index(idx)
        mock_supabase_client.table.assert_called_with("market_indices")
```

- [ ] **Step 4: 테스트 실패 확인**

Run: `cd backend && python -m pytest tests/services/test_supabase.py -v`
Expected: FAIL

- [ ] **Step 5: Supabase 클라이언트 구현**

```python
# backend/app/services/supabase.py
from supabase import create_client, Client

from app.config import Settings
from app.models.market import MarketIndex, Sector, EconomicIndicator
from app.models.news import NewsArticle


class SupabaseService:
    def __init__(self, settings: Settings) -> None:
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key,
        )

    def insert_market_index(self, index: MarketIndex) -> dict:
        return (
            self.client.table("market_indices")
            .insert(index.model_dump(mode="json"))
            .execute()
        )

    def insert_sector(self, sector: Sector) -> dict:
        return (
            self.client.table("sectors")
            .insert(sector.model_dump(mode="json"))
            .execute()
        )

    def insert_news_article(self, article: NewsArticle) -> dict:
        return (
            self.client.table("news_articles")
            .upsert(article.model_dump(mode="json"), on_conflict="url")
            .execute()
        )

    def insert_economic_indicator(self, indicator: EconomicIndicator) -> dict:
        return (
            self.client.table("economic_indicators")
            .insert(indicator.model_dump(mode="json"))
            .execute()
        )

    def get_latest_regime(self) -> dict | None:
        result = (
            self.client.table("macro_regimes")
            .select("*")
            .order("analyzed_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    def get_sector_mapping(self) -> list[dict]:
        result = (
            self.client.table("sector_regime_mapping")
            .select("*")
            .order("display_order")
            .execute()
        )
        return result.data

    def get_latest_scoreboards(self, batch_type: str) -> list[dict]:
        result = (
            self.client.table("sector_scoreboards")
            .select("*")
            .eq("batch_type", batch_type)
            .order("scored_at", desc=True)
            .limit(12)
            .execute()
        )
        return result.data
```

- [ ] **Step 6: 테스트 통과 확인**

Run: `cd backend && python -m pytest tests/services/test_supabase.py -v`
Expected: 2 passed

- [ ] **Step 7: Commit**

```bash
git add backend/supabase/ backend/app/services/supabase.py backend/tests/services/test_supabase.py backend/tests/conftest.py
git commit -m "feat: add Supabase migration schema and service client"
```

---

## Task 5: EODHD API 클라이언트

**Files:**
- Create: `backend/app/services/eodhd.py`
- Create: `backend/tests/services/test_eodhd.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# backend/tests/services/test_eodhd.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal
import httpx


MOCK_EOD_RESPONSE = {
    "close": 5200.50,
    "change_p": 0.55,
    "volume": 80000000,
}

MOCK_HISTORICAL_RESPONSE = [
    {"date": "2026-04-04", "close": 5200.50, "volume": 80000000},
    {"date": "2026-03-28", "close": 5150.00, "volume": 75000000},
    {"date": "2026-03-05", "close": 5050.00, "volume": 70000000},
    {"date": "2026-01-05", "close": 4900.00, "volume": 65000000},
    {"date": "2025-10-05", "close": 4700.00, "volume": 60000000},
]


@pytest.fixture
def eodhd_service(mock_settings):
    from app.services.eodhd import EODHDService
    return EODHDService(mock_settings)


@pytest.mark.asyncio
async def test_fetch_realtime_quote(eodhd_service):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_EOD_RESPONSE
    mock_response.raise_for_status = MagicMock()

    with patch.object(eodhd_service.client, "get", new_callable=AsyncMock, return_value=mock_response):
        result = await eodhd_service.fetch_realtime_quote("SPY.US")
        assert result["close"] == 5200.50


@pytest.mark.asyncio
async def test_fetch_sector_etfs(eodhd_service):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_EOD_RESPONSE
    mock_response.raise_for_status = MagicMock()

    with patch.object(eodhd_service.client, "get", new_callable=AsyncMock, return_value=mock_response):
        results = await eodhd_service.fetch_sector_etfs()
        assert len(results) > 0
        assert "XLK" in [r["symbol"] for r in results]


@pytest.mark.asyncio
async def test_calculate_momentum(eodhd_service):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_HISTORICAL_RESPONSE
    mock_response.raise_for_status = MagicMock()

    with patch.object(eodhd_service.client, "get", new_callable=AsyncMock, return_value=mock_response):
        momentum = await eodhd_service.calculate_momentum("XLK.US")
        assert "momentum_1w" in momentum
        assert "momentum_1m" in momentum
        assert "momentum_3m" in momentum
        assert "momentum_6m" in momentum
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd backend && python -m pytest tests/services/test_eodhd.py -v`
Expected: FAIL

- [ ] **Step 3: EODHD 클라이언트 구현**

```python
# backend/app/services/eodhd.py
import httpx

from app.config import Settings

SECTOR_ETFS = [
    ("Financials", "XLF"),
    ("Real Estate", "XLRE"),
    ("Technology", "XLK"),
    ("Consumer Discretionary", "XLY"),
    ("Industrials", "XLI"),
    ("Materials", "XLB"),
    ("Energy", "XLE"),
    ("Utilities", "XLU"),
    ("Healthcare", "XLV"),
    ("Consumer Staples", "XLP"),
]

INDEX_SYMBOLS = [
    ("S&P 500", "SPY"),
    ("NASDAQ", "QQQ"),
    ("DOW", "DIA"),
]


class EODHDService:
    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.eodhd_api_key
        self.base_url = settings.eodhd_base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def fetch_realtime_quote(self, symbol: str) -> dict:
        resp = await self.client.get(
            f"{self.base_url}/real-time/{symbol}",
            params={"api_token": self.api_key, "fmt": "json"},
        )
        resp.raise_for_status()
        return resp.json()

    async def fetch_historical(self, symbol: str, period: str = "d", limit: int = 180) -> list[dict]:
        resp = await self.client.get(
            f"{self.base_url}/eod/{symbol}",
            params={
                "api_token": self.api_key,
                "fmt": "json",
                "period": period,
                "order": "d",
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data[:limit]

    async def fetch_sector_etfs(self) -> list[dict]:
        results = []
        for name, symbol in SECTOR_ETFS:
            quote = await self.fetch_realtime_quote(f"{symbol}.US")
            results.append({
                "symbol": symbol,
                "name": name,
                "close": quote.get("close", 0),
                "change_p": quote.get("change_p", 0),
                "volume": quote.get("volume", 0),
            })
        return results

    async def fetch_indices(self) -> list[dict]:
        results = []
        for name, symbol in INDEX_SYMBOLS:
            quote = await self.fetch_realtime_quote(f"{symbol}.US")
            results.append({
                "symbol": symbol,
                "name": name,
                "close": quote.get("close", 0),
                "change_p": quote.get("change_p", 0),
            })
        return results

    async def calculate_momentum(self, symbol: str) -> dict:
        history = await self.fetch_historical(symbol, limit=180)
        if not history:
            return {"momentum_1w": 0, "momentum_1m": 0, "momentum_3m": 0, "momentum_6m": 0}

        current = history[0]["close"]
        def pct(idx: int) -> float:
            if idx < len(history) and history[idx]["close"]:
                return round((current - history[idx]["close"]) / history[idx]["close"] * 100, 2)
            return 0.0

        return {
            "momentum_1w": pct(min(5, len(history) - 1)),
            "momentum_1m": pct(min(22, len(history) - 1)),
            "momentum_3m": pct(min(66, len(history) - 1)),
            "momentum_6m": pct(min(132, len(history) - 1)),
        }

    async def close(self) -> None:
        await self.client.aclose()
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd backend && python -m pytest tests/services/test_eodhd.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/eodhd.py backend/tests/services/test_eodhd.py
git commit -m "feat: add EODHD API client with momentum calculation"
```

---

## Task 6: NewsAPI 클라이언트

**Files:**
- Create: `backend/app/services/newsapi.py`
- Create: `backend/tests/services/test_newsapi.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# backend/tests/services/test_newsapi.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

MOCK_NEWSAPI_RESPONSE = {
    "status": "ok",
    "totalResults": 3,
    "articles": [
        {
            "title": "Fed Decision Today",
            "source": {"name": "Reuters"},
            "url": "https://reuters.com/1",
            "publishedAt": "2026-04-05T08:00:00Z",
            "description": "Federal Reserve meeting today...",
        },
        {
            "title": "Tech Earnings Beat",
            "source": {"name": "CNBC"},
            "url": "https://cnbc.com/2",
            "publishedAt": "2026-04-05T07:00:00Z",
            "description": "Major tech companies beat...",
        },
        {
            "title": "Oil Prices Surge",
            "source": {"name": "Bloomberg"},
            "url": "https://bloomberg.com/3",
            "publishedAt": "2026-04-05T06:00:00Z",
            "description": "Oil prices surge on...",
        },
    ],
}


@pytest.fixture
def newsapi_service(mock_settings):
    from app.services.newsapi import NewsAPIService
    return NewsAPIService(mock_settings)


@pytest.mark.asyncio
async def test_fetch_top_headlines(newsapi_service):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_NEWSAPI_RESPONSE
    mock_response.raise_for_status = MagicMock()

    with patch.object(newsapi_service.client, "get", new_callable=AsyncMock, return_value=mock_response):
        articles = await newsapi_service.fetch_top_headlines("business")
        assert len(articles) == 3
        assert articles[0]["title"] == "Fed Decision Today"


@pytest.mark.asyncio
async def test_fetch_all_categories(newsapi_service):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_NEWSAPI_RESPONSE
    mock_response.raise_for_status = MagicMock()

    with patch.object(newsapi_service.client, "get", new_callable=AsyncMock, return_value=mock_response):
        result = await newsapi_service.fetch_all_categories(top_n=3)
        assert len(result) == 4  # 4 categories
        for category, articles in result.items():
            assert len(articles) <= 3


@pytest.mark.asyncio
async def test_handles_rate_limit(newsapi_service):
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.raise_for_status.side_effect = Exception("Rate limit exceeded")

    with patch.object(newsapi_service.client, "get", new_callable=AsyncMock, return_value=mock_response):
        with pytest.raises(Exception, match="Rate limit"):
            await newsapi_service.fetch_top_headlines("business")
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd backend && python -m pytest tests/services/test_newsapi.py -v`
Expected: FAIL

- [ ] **Step 3: NewsAPI 클라이언트 구현**

```python
# backend/app/services/newsapi.py
import httpx

from app.config import Settings

NEWSAPI_BASE_URL = "https://newsapi.org/v2"

# PRD 카테고리 → NewsAPI 카테고리 매핑
CATEGORY_MAP = {
    "politics": "general",      # 정치 → general (country=us 필터로 미국 뉴스)
    "business": "business",     # 경제
    "society": "science",       # 사회 → science/health
    "world": "technology",      # 글로벌 → technology (global tech news)
}


class NewsAPIService:
    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.newsapi_key
        self.client = httpx.AsyncClient(timeout=15.0)

    async def fetch_top_headlines(
        self,
        category: str,
        country: str = "us",
        page_size: int = 5,
    ) -> list[dict]:
        resp = await self.client.get(
            f"{NEWSAPI_BASE_URL}/top-headlines",
            params={
                "apiKey": self.api_key,
                "category": category,
                "country": country,
                "pageSize": page_size,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("articles", [])

    async def fetch_all_categories(self, top_n: int = 3) -> dict[str, list[dict]]:
        results = {}
        for label, api_category in CATEGORY_MAP.items():
            articles = await self.fetch_top_headlines(api_category, page_size=top_n)
            results[label] = articles[:top_n]
        return results

    async def close(self) -> None:
        await self.client.aclose()
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd backend && python -m pytest tests/services/test_newsapi.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/newsapi.py backend/tests/services/test_newsapi.py
git commit -m "feat: add NewsAPI client with category mapping"
```

---

## Task 7: RSS Fallback 클라이언트

**Files:**
- Create: `backend/app/services/rss_fallback.py`
- Create: `backend/tests/services/test_rss_fallback.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# backend/tests/services/test_rss_fallback.py
import pytest
from unittest.mock import patch, MagicMock


MOCK_RSS_FEED = MagicMock()
MOCK_RSS_FEED.entries = [
    MagicMock(
        title="Economy News 1",
        link="https://news.google.com/1",
        published="Sat, 05 Apr 2026 08:00:00 GMT",
        source=MagicMock(title="Reuters"),
    ),
    MagicMock(
        title="Economy News 2",
        link="https://news.google.com/2",
        published="Sat, 05 Apr 2026 07:00:00 GMT",
        source=MagicMock(title="AP"),
    ),
    MagicMock(
        title="Economy News 3",
        link="https://news.google.com/3",
        published="Sat, 05 Apr 2026 06:00:00 GMT",
        source=MagicMock(title="CNBC"),
    ),
]
MOCK_RSS_FEED.bozo = False


def test_fetch_google_news_rss():
    from app.services.rss_fallback import RSSFallbackService

    with patch("app.services.rss_fallback.feedparser.parse", return_value=MOCK_RSS_FEED):
        service = RSSFallbackService()
        articles = service.fetch_news(top_n=3)
        assert len(articles) == 3
        assert articles[0]["title"] == "Economy News 1"
        assert articles[0]["source"] == "Reuters"


def test_handles_empty_feed():
    from app.services.rss_fallback import RSSFallbackService

    empty_feed = MagicMock()
    empty_feed.entries = []
    empty_feed.bozo = False

    with patch("app.services.rss_fallback.feedparser.parse", return_value=empty_feed):
        service = RSSFallbackService()
        articles = service.fetch_news()
        assert articles == []


def test_handles_parse_error():
    from app.services.rss_fallback import RSSFallbackService

    error_feed = MagicMock()
    error_feed.entries = []
    error_feed.bozo = True
    error_feed.bozo_exception = Exception("Parse error")

    with patch("app.services.rss_fallback.feedparser.parse", return_value=error_feed):
        service = RSSFallbackService()
        articles = service.fetch_news()
        assert articles == []
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd backend && python -m pytest tests/services/test_rss_fallback.py -v`
Expected: FAIL

- [ ] **Step 3: RSS Fallback 구현**

```python
# backend/app/services/rss_fallback.py
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
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `cd backend && python -m pytest tests/services/test_rss_fallback.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/rss_fallback.py backend/tests/services/test_rss_fallback.py
git commit -m "feat: add Google News RSS fallback service"
```

---

## Task 8: FastAPI 앱 + 헬스체크 엔드포인트

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/api/deps.py`
- Create: `backend/app/api/routes/health.py`
- Create: `backend/tests/api/test_health.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# backend/tests/api/test_health.py
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(mock_settings):
    from app.main import app
    from app.api.deps import get_settings

    app.dependency_overrides[get_settings] = lambda: mock_settings
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_redirects_or_returns_info(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "name" in data
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `cd backend && python -m pytest tests/api/test_health.py -v`
Expected: FAIL

- [ ] **Step 3: deps.py 구현**

```python
# backend/app/api/deps.py
from functools import lru_cache

from app.config import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 4: health.py 라우트 구현**

```python
# backend/app/api/routes/health.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "economi-analyzer-backend",
    }
```

- [ ] **Step 5: main.py 구현**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router

app = FastAPI(
    title="Economi Analyzer API",
    description="AI-Driven Market Insights Dashboard - Sector Rotation Analysis",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)


@app.get("/")
def root():
    return {
        "name": "Economi Analyzer API",
        "version": "0.1.0",
        "docs": "/docs",
    }
```

- [ ] **Step 6: 테스트 통과 확인**

Run: `cd backend && python -m pytest tests/api/test_health.py -v`
Expected: 2 passed

- [ ] **Step 7: 전체 테스트 실행**

Run: `cd backend && python -m pytest -v --tb=short`
Expected: All tests passed (약 17개)

- [ ] **Step 8: Commit**

```bash
git add backend/app/main.py backend/app/api/deps.py backend/app/api/routes/health.py backend/tests/api/test_health.py
git commit -m "feat: add FastAPI app with health check endpoint"
```

---

## Task 9: MCP 서버 등록 + 프로젝트 루트 설정

**Files:**
- Create: `.mcp.json` (프로젝트 루트)

- [ ] **Step 1: .mcp.json 작성**

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
    }
  }
}
```

> NewsAPI MCP 서버는 Phase 2에서 구현 후 추가

- [ ] **Step 2: git 루트 .gitignore 업데이트**

`.gitignore` 프로젝트 루트에 생성:
```gitignore
# Environment
.env
backend/.env

# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/
.pytest_cache/
.ruff_cache/
.coverage

# Node
node_modules/
.next/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 3: Commit**

```bash
git add .mcp.json .gitignore
git commit -m "chore: add MCP server config and root gitignore"
```

---

## Phase 1 완료 기준

모든 태스크 완료 후 아래를 확인:

```bash
cd backend && python -m pytest -v --tb=short
```

Expected:
- `test_config.py` — 2 passed
- `test_models.py` — 7 passed
- `test_eodhd.py` — 3 passed
- `test_newsapi.py` — 3 passed
- `test_rss_fallback.py` — 3 passed
- `test_supabase.py` — 2 passed
- `test_health.py` — 2 passed
- **Total: ~22 passed, 0 failed**

```bash
cd backend && uvicorn app.main:app --reload --port 8000
# → http://localhost:8000/docs 에서 Swagger UI 확인
# → http://localhost:8000/health → {"status": "healthy"}
```

---

## 다음 Phase

Phase 1 완료 후 → **Phase 2: AI Pipeline** (LangGraph 그래프 + 3개 에이전트 + NewsAPI MCP 서버)
