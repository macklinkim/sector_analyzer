# Phase 3: API + Scheduler — FastAPI 엔드포인트 + APScheduler 배치 작업

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 프론트엔드 대시보드가 소비할 REST API 엔드포인트 3개(market, news, analysis) 구현 + APScheduler 기반 1일 2회 배치 스케줄러 구현. Phase 2의 LangGraph 파이프라인을 스케줄러가 트리거하고, 결과를 Supabase에 저장하며, API가 최신 데이터를 조회하여 프론트엔드에 제공.

**Architecture:** FastAPI 라우터 3개(market, news, analysis)가 Supabase에서 최신 배치 결과를 조회. APScheduler가 08:30 ET / 17:00 ET에 LangGraph 파이프라인을 실행. Supabase 서비스에 조회 메서드 추가. 수동 트리거 엔드포인트도 제공.

**Tech Stack:** FastAPI, APScheduler, pydantic v2 (기존), supabase-py (기존), langgraph (기존)

**Spec:** `docs/superpowers/specs/2026-04-05-market-insights-dashboard-design.md`
**Phase 1 Plan:** `docs/superpowers/plans/2026-04-05-phase1-foundation.md`
**Phase 2 Plan:** `docs/superpowers/plans/2026-04-05-phase2-ai-pipeline.md`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `backend/pyproject.toml` | APScheduler 의존성 추가 |
| Modify | `backend/app/services/supabase.py` | 프론트엔드용 조회 메서드 추가 |
| Create | `backend/app/api/routes/market.py` | 섹터/지수/경제지표 엔드포인트 |
| Create | `backend/app/api/routes/news.py` | 뉴스 + Impact Score 엔드포인트 |
| Create | `backend/app/api/routes/analysis.py` | AI 분석 리포트 엔드포인트 |
| Modify | `backend/app/main.py` | 라우터 등록 + 스케줄러 lifespan |
| Create | `backend/app/scheduler/jobs.py` | APScheduler 배치 작업 정의 |
| Create | `backend/tests/services/test_supabase_queries.py` | 조회 메서드 테스트 |
| Create | `backend/tests/api/__init__.py` (이미 존재 시 skip) | 테스트 패키지 |
| Create | `backend/tests/api/test_market.py` | Market API 테스트 |
| Create | `backend/tests/api/test_news.py` | News API 테스트 |
| Create | `backend/tests/api/test_analysis.py` | Analysis API 테스트 |
| Create | `backend/tests/scheduler/__init__.py` | 스케줄러 테스트 패키지 |
| Create | `backend/tests/scheduler/test_jobs.py` | 스케줄러 작업 테스트 |

---

## Task 1: APScheduler 의존성 추가

**Files:**
- Modify: `backend/pyproject.toml`

- [ ] **Step 1: pyproject.toml에 APScheduler 추가**

`dependencies` 리스트에 추가:
```toml
    "apscheduler>=3.10.0,<4.0.0",
```

> APScheduler 3.x 사용 (4.x는 API 호환 불가). AsyncIOScheduler 지원.

- [ ] **Step 2: 설치**

```bash
cd backend && .venv/Scripts/pip install -e ".[dev]"
```

Expected: 성공, `apscheduler` 패키지 설치됨

- [ ] **Step 3: 커밋**

```bash
git add backend/pyproject.toml
git commit -m "feat: add APScheduler dependency for batch scheduling"
```

---

## Task 2: Supabase 조회 메서드 확장

**Files:**
- Modify: `backend/app/services/supabase.py`
- Create: `backend/tests/services/test_supabase_queries.py`

- [ ] **Step 1: 테스트 파일 작성**

```python
# backend/tests/services/test_supabase_queries.py
from unittest.mock import MagicMock
from app.services.supabase import SupabaseService


def _make_service(mock_client: MagicMock) -> SupabaseService:
    svc = object.__new__(SupabaseService)
    svc.client = mock_client
    return svc


def test_get_latest_indices(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"symbol": "SPY", "name": "S&P 500", "price": "500.0", "change_percent": "0.5"}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_indices()
    assert len(result) == 1
    assert result[0]["symbol"] == "SPY"
    mock_supabase_client.table.assert_called_with("market_indices")


def test_get_latest_sectors(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"name": "Technology", "etf_symbol": "XLK", "change_percent": "1.2"}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_sectors()
    assert len(result) == 1
    assert result[0]["name"] == "Technology"


def test_get_latest_economic_indicators(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"indicator_name": "US10Y", "value": "4.25"}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_economic_indicators()
    assert len(result) == 1


def test_get_latest_news_articles(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"title": "Fed holds rates", "category": "business"}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_news_articles(limit=20)
    assert len(result) == 1


def test_get_news_by_category(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"title": "Tech earnings", "category": "business"}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_news_by_category("business", limit=10)
    assert len(result) == 1


def test_get_latest_news_impacts(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"sector_name": "Technology", "impact_score": 7.5}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_news_impacts()
    assert len(result) == 1


def test_get_latest_report(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"batch_type": "pre_market", "summary": "Bullish outlook"}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_report()
    assert result is not None
    assert result["summary"] == "Bullish outlook"


def test_get_latest_report_empty(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = []
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_report()
    assert result is None


def test_get_latest_rotation_signals(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"signal_type": "rotate_in", "to_sector": "Technology"}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_rotation_signals()
    assert len(result) == 1
```

- [ ] **Step 2: 테스트 실행 → 실패 확인**

```bash
cd backend && python -m pytest tests/services/test_supabase_queries.py -v
```

Expected: FAIL — `get_latest_indices`, `get_latest_sectors` 등 메서드 미존재

- [ ] **Step 3: supabase.py에 조회 메서드 추가**

`backend/app/services/supabase.py`에 다음 메서드 추가:

```python
    # --- 프론트엔드용 조회 메서드 ---

    def get_latest_indices(self) -> list[dict]:
        result = (
            self.client.table("market_indices")
            .select("*")
            .order("collected_at", desc=True)
            .limit(10)
            .execute()
        )
        return result.data

    def get_latest_sectors(self) -> list[dict]:
        result = (
            self.client.table("sectors")
            .select("*")
            .order("collected_at", desc=True)
            .limit(12)
            .execute()
        )
        return result.data

    def get_latest_economic_indicators(self) -> list[dict]:
        result = (
            self.client.table("economic_indicators")
            .select("*")
            .order("reported_at", desc=True)
            .limit(10)
            .execute()
        )
        return result.data

    def get_latest_news_articles(self, limit: int = 20) -> list[dict]:
        result = (
            self.client.table("news_articles")
            .select("*")
            .order("published_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data

    def get_news_by_category(self, category: str, limit: int = 10) -> list[dict]:
        result = (
            self.client.table("news_articles")
            .select("*")
            .eq("category", category)
            .order("published_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data

    def get_latest_news_impacts(self) -> list[dict]:
        result = (
            self.client.table("news_impact_analyses")
            .select("*")
            .order("analyzed_at", desc=True)
            .limit(50)
            .execute()
        )
        return result.data

    def get_latest_report(self) -> dict | None:
        result = (
            self.client.table("market_reports")
            .select("*")
            .order("analyzed_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    def get_latest_rotation_signals(self) -> list[dict]:
        result = (
            self.client.table("rotation_signals")
            .select("*")
            .order("detected_at", desc=True)
            .limit(20)
            .execute()
        )
        return result.data
```

- [ ] **Step 4: 테스트 실행 → 통과 확인**

```bash
cd backend && python -m pytest tests/services/test_supabase_queries.py -v
```

Expected: ALL PASSED

- [ ] **Step 5: 커밋**

```bash
git add backend/app/services/supabase.py backend/tests/services/test_supabase_queries.py
git commit -m "feat: add Supabase query methods for frontend API"
```

---

## Task 3: Market API 라우터

**Files:**
- Modify: `backend/app/api/deps.py`
- Create: `backend/app/api/routes/market.py`
- Create: `backend/tests/api/test_market.py`

> **테스트 패턴**: 기존 `test_health.py`와 동일하게 `dependency_overrides` + `client` fixture 사용.
> 라우터는 `Depends(get_supabase)`로 서비스를 주입받아 테스트에서 override 가능.

- [ ] **Step 1: deps.py에 Supabase 의존성 추가**

`backend/app/api/deps.py`에 추가:

```python
from app.services.supabase import SupabaseService


def get_supabase() -> SupabaseService:
    settings = get_settings()
    return SupabaseService(settings)
```

- [ ] **Step 2: 테스트 작성**

```python
# backend/tests/api/test_market.py
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def mock_supabase_svc():
    return MagicMock()


@pytest.fixture
def client(mock_settings, mock_supabase_svc):
    from app.main import app
    from app.api.deps import get_settings, get_supabase

    app.dependency_overrides[get_settings] = lambda: mock_settings
    app.dependency_overrides[get_supabase] = lambda: mock_supabase_svc
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_indices(client, mock_supabase_svc):
    mock_supabase_svc.get_latest_indices.return_value = [
        {"symbol": "SPY", "name": "S&P 500", "price": "500.0", "change_percent": "0.5"}
    ]
    response = client.get("/api/market/indices")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["symbol"] == "SPY"


def test_get_sectors(client, mock_supabase_svc):
    mock_supabase_svc.get_latest_sectors.return_value = [
        {"name": "Technology", "etf_symbol": "XLK", "change_percent": "1.2"}
    ]
    response = client.get("/api/market/sectors")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Technology"


def test_get_economic_indicators(client, mock_supabase_svc):
    mock_supabase_svc.get_latest_economic_indicators.return_value = [
        {"indicator_name": "US10Y", "value": "4.25"}
    ]
    response = client.get("/api/market/indicators")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["indicator_name"] == "US10Y"


def test_get_regime(client, mock_supabase_svc):
    mock_supabase_svc.get_latest_regime.return_value = {
        "regime": "goldilocks", "reasoning": "Growth up, inflation stable"
    }
    response = client.get("/api/market/regime")
    assert response.status_code == 200
    data = response.json()
    assert data["regime"] == "goldilocks"


def test_get_regime_none(client, mock_supabase_svc):
    mock_supabase_svc.get_latest_regime.return_value = None
    response = client.get("/api/market/regime")
    assert response.status_code == 404
```

- [ ] **Step 3: 테스트 실행 → 실패 확인**

```bash
cd backend && python -m pytest tests/api/test_market.py -v
```

Expected: FAIL — market 라우터 미존재 (또는 `/api/market/indices` 404)

- [ ] **Step 4: market.py 라우터 구현**

```python
# backend/app/api/routes/market.py
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_supabase
from app.services.supabase import SupabaseService

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/indices")
def get_indices(svc: SupabaseService = Depends(get_supabase)):
    return svc.get_latest_indices()


@router.get("/sectors")
def get_sectors(svc: SupabaseService = Depends(get_supabase)):
    return svc.get_latest_sectors()


@router.get("/indicators")
def get_economic_indicators(svc: SupabaseService = Depends(get_supabase)):
    return svc.get_latest_economic_indicators()


@router.get("/regime")
def get_regime(svc: SupabaseService = Depends(get_supabase)):
    regime = svc.get_latest_regime()
    if regime is None:
        raise HTTPException(status_code=404, detail="No regime data available")
    return regime
```

- [ ] **Step 5: main.py에 market 라우터 등록**

`backend/app/main.py`에 import 및 include 추가:

```python
from app.api.routes.market import router as market_router
# ...
app.include_router(market_router)
```

- [ ] **Step 6: 테스트 실행 → 통과 확인**

```bash
cd backend && python -m pytest tests/api/test_market.py -v
```

Expected: ALL PASSED

- [ ] **Step 7: 커밋**

```bash
git add backend/app/api/routes/market.py backend/app/api/deps.py backend/app/main.py backend/tests/api/test_market.py
git commit -m "feat: add market API endpoints (indices, sectors, indicators, regime)"
```

---

## Task 4: News API 라우터

**Files:**
- Create: `backend/app/api/routes/news.py`
- Create: `backend/tests/api/test_news.py`

- [ ] **Step 1: 테스트 작성**

```python
# backend/tests/api/test_news.py
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def mock_supabase_svc():
    return MagicMock()


@pytest.fixture
def client(mock_settings, mock_supabase_svc):
    from app.main import app
    from app.api.deps import get_settings, get_supabase

    app.dependency_overrides[get_settings] = lambda: mock_settings
    app.dependency_overrides[get_supabase] = lambda: mock_supabase_svc
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_news_all(client, mock_supabase_svc):
    mock_supabase_svc.get_latest_news_articles.return_value = [
        {"title": "Fed holds rates", "category": "business"}
    ]
    response = client.get("/api/news/articles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_get_news_by_category(client, mock_supabase_svc):
    mock_supabase_svc.get_news_by_category.return_value = [
        {"title": "Tech earnings", "category": "business"}
    ]
    response = client.get("/api/news/articles?category=business")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_get_news_impacts(client, mock_supabase_svc):
    mock_supabase_svc.get_latest_news_impacts.return_value = [
        {"sector_name": "Technology", "impact_score": 7.5}
    ]
    response = client.get("/api/news/impacts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["impact_score"] == 7.5
```

- [ ] **Step 2: 테스트 실행 → 실패 확인**

```bash
cd backend && python -m pytest tests/api/test_news.py -v
```

Expected: FAIL — news 라우터 미존재

- [ ] **Step 3: news.py 라우터 구현**

```python
# backend/app/api/routes/news.py
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
```

- [ ] **Step 4: main.py에 news 라우터 등록**

`backend/app/main.py`에 추가:

```python
from app.api.routes.news import router as news_router
# ...
app.include_router(news_router)
```

- [ ] **Step 5: 테스트 실행 → 통과 확인**

```bash
cd backend && python -m pytest tests/api/test_news.py -v
```

Expected: ALL PASSED

- [ ] **Step 6: 커밋**

```bash
git add backend/app/api/routes/news.py backend/app/main.py backend/tests/api/test_news.py
git commit -m "feat: add news API endpoints (articles with category filter, impacts)"
```

---

## Task 5: Analysis API 라우터

**Files:**
- Create: `backend/app/api/routes/analysis.py`
- Create: `backend/tests/api/test_analysis.py`

- [ ] **Step 1: 테스트 작성**

```python
# backend/tests/api/test_analysis.py
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def mock_supabase_svc():
    return MagicMock()


@pytest.fixture
def client(mock_settings, mock_supabase_svc):
    from app.main import app
    from app.api.deps import get_settings, get_supabase

    app.dependency_overrides[get_settings] = lambda: mock_settings
    app.dependency_overrides[get_supabase] = lambda: mock_supabase_svc
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_report(client, mock_supabase_svc):
    mock_supabase_svc.get_latest_report.return_value = {
        "batch_type": "pre_market",
        "summary": "Bullish outlook",
        "disclaimer": "본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다.",
    }
    response = client.get("/api/analysis/report")
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Bullish outlook"
    assert "투자" in data["disclaimer"]


def test_get_report_none(client, mock_supabase_svc):
    mock_supabase_svc.get_latest_report.return_value = None
    response = client.get("/api/analysis/report")
    assert response.status_code == 404


def test_get_scoreboards(client, mock_supabase_svc):
    mock_supabase_svc.get_latest_scoreboards.return_value = [
        {"sector_name": "Technology", "final_score": "0.85", "rank": 1}
    ]
    response = client.get("/api/analysis/scoreboards?batch_type=pre_market")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["rank"] == 1


def test_get_rotation_signals(client, mock_supabase_svc):
    mock_supabase_svc.get_latest_rotation_signals.return_value = [
        {"signal_type": "rotate_in", "to_sector": "Technology", "strength": "0.8"}
    ]
    response = client.get("/api/analysis/signals")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["signal_type"] == "rotate_in"


def test_trigger_pipeline(client):
    with patch("app.api.routes.analysis.run_pipeline") as mock_run:
        mock_run.return_value = {
            "status": "completed",
            "batch_type": "manual",
        }
        response = client.post("/api/analysis/trigger")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
```

- [ ] **Step 2: 테스트 실행 → 실패 확인**

```bash
cd backend && python -m pytest tests/api/test_analysis.py -v
```

Expected: FAIL — analysis 라우터 미존재

- [ ] **Step 3: analysis.py 라우터 구현**

```python
# backend/app/api/routes/analysis.py
import logging
from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_supabase
from app.services.supabase import SupabaseService
from app.agents.graph import build_graph
from app.agents.state import create_initial_state

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


def run_pipeline(batch_type: str = "manual") -> dict:
    graph = build_graph()
    initial_state = create_initial_state(batch_type)
    graph.invoke(initial_state)
    return {"status": "completed", "batch_type": batch_type}


@router.get("/report")
def get_report(svc: SupabaseService = Depends(get_supabase)):
    report = svc.get_latest_report()
    if report is None:
        raise HTTPException(status_code=404, detail="No report available")
    return report


@router.get("/scoreboards")
def get_scoreboards(
    batch_type: str = Query("pre_market", description="Batch type: pre_market or post_market"),
    svc: SupabaseService = Depends(get_supabase),
):
    return svc.get_latest_scoreboards(batch_type)


@router.get("/signals")
def get_rotation_signals(svc: SupabaseService = Depends(get_supabase)):
    return svc.get_latest_rotation_signals()


@router.post("/trigger")
def trigger_pipeline():
    try:
        result = run_pipeline("manual")
        return result
    except Exception as e:
        logger.exception("Pipeline trigger failed")
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")
```

- [ ] **Step 4: main.py에 analysis 라우터 등록**

`backend/app/main.py`에 추가:

```python
from app.api.routes.analysis import router as analysis_router
# ...
app.include_router(analysis_router)
```

- [ ] **Step 5: 테스트 실행 → 통과 확인**

```bash
cd backend && python -m pytest tests/api/test_analysis.py -v
```

Expected: ALL PASSED

- [ ] **Step 6: 커밋**

```bash
git add backend/app/api/routes/analysis.py backend/app/main.py backend/tests/api/test_analysis.py
git commit -m "feat: add analysis API endpoints (report, scoreboards, signals, manual trigger)"
```

---

## Task 6: APScheduler 배치 작업

**Files:**
- Create: `backend/app/scheduler/jobs.py`
- Create: `backend/tests/scheduler/__init__.py`
- Create: `backend/tests/scheduler/test_jobs.py`

- [ ] **Step 1: 테스트 디렉토리 생성**

```bash
mkdir -p backend/tests/scheduler
touch backend/tests/scheduler/__init__.py
```

- [ ] **Step 2: 테스트 작성**

```python
# backend/tests/scheduler/test_jobs.py
from unittest.mock import patch, MagicMock
from app.scheduler.jobs import run_batch, create_scheduler


def test_run_batch_pre_market():
    with patch("app.scheduler.jobs.build_graph") as mock_build:
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {"batch_type": "pre_market"}
        mock_build.return_value = mock_graph

        result = run_batch("pre_market")

        mock_build.assert_called_once()
        mock_graph.invoke.assert_called_once()
        assert result["batch_type"] == "pre_market"


def test_run_batch_post_market():
    with patch("app.scheduler.jobs.build_graph") as mock_build:
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {"batch_type": "post_market"}
        mock_build.return_value = mock_graph

        result = run_batch("post_market")
        assert result["batch_type"] == "post_market"


def test_run_batch_handles_error():
    with patch("app.scheduler.jobs.build_graph") as mock_build:
        mock_build.side_effect = RuntimeError("API down")
        result = run_batch("pre_market")
        assert result["status"] == "failed"
        assert "API down" in result["error"]


def test_create_scheduler():
    scheduler = create_scheduler()
    jobs = scheduler.get_jobs()
    assert len(jobs) == 2
    job_names = [j.name for j in jobs]
    assert "pre_market_batch" in job_names
    assert "post_market_batch" in job_names
```

- [ ] **Step 3: 테스트 실행 → 실패 확인**

```bash
cd backend && python -m pytest tests/scheduler/test_jobs.py -v
```

Expected: FAIL — `app.scheduler.jobs` 모듈 미존재

- [ ] **Step 4: jobs.py 구현**

```python
# backend/app/scheduler/jobs.py
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.agents.graph import build_graph
from app.agents.state import create_initial_state

logger = logging.getLogger(__name__)


def run_batch(batch_type: str) -> dict:
    logger.info("Starting %s batch at %s", batch_type, datetime.now(timezone.utc).isoformat())
    try:
        graph = build_graph()
        initial_state = create_initial_state(batch_type)
        result = graph.invoke(initial_state)
        logger.info("Completed %s batch", batch_type)
        return result
    except Exception as e:
        logger.exception("Batch %s failed", batch_type)
        return {"batch_type": batch_type, "status": "failed", "error": str(e)}


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="US/Eastern")

    scheduler.add_job(
        run_batch,
        trigger=CronTrigger(hour=8, minute=30, timezone="US/Eastern"),
        args=["pre_market"],
        id="pre_market_batch",
        name="pre_market_batch",
        replace_existing=True,
    )

    scheduler.add_job(
        run_batch,
        trigger=CronTrigger(hour=17, minute=0, timezone="US/Eastern"),
        args=["post_market"],
        id="post_market_batch",
        name="post_market_batch",
        replace_existing=True,
    )

    return scheduler
```

- [ ] **Step 5: 테스트 실행 → 통과 확인**

```bash
cd backend && python -m pytest tests/scheduler/test_jobs.py -v
```

Expected: ALL PASSED

- [ ] **Step 6: 커밋**

```bash
git add backend/app/scheduler/jobs.py backend/tests/scheduler/__init__.py backend/tests/scheduler/test_jobs.py
git commit -m "feat: add APScheduler batch jobs (pre_market 08:30, post_market 17:00 ET)"
```

---

## Task 7: main.py에 스케줄러 lifespan 통합

**Files:**
- Modify: `backend/app/main.py`
- Modify: `backend/tests/api/test_health.py` (스케줄러 상태 확인 추가)

- [ ] **Step 1: main.py에 lifespan + 스케줄러 통합**

`backend/app/main.py`를 다음으로 교체:

> **핵심 변경**: `create_scheduler()`를 모듈 레벨이 아닌 `lifespan` 내부에서 호출.
> 모듈 레벨에서 호출하면 테스트 시 import만으로 스케줄러가 생성되어 불필요한 의존성 로딩 발생.

```python
# backend/app/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.market import router as market_router
from app.api.routes.news import router as news_router
from app.api.routes.analysis import router as analysis_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.scheduler.jobs import create_scheduler

    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Scheduler started with jobs: %s", [j.name for j in scheduler.get_jobs()])
    yield
    scheduler.shutdown(wait=False)
    logger.info("Scheduler shut down")


app = FastAPI(
    title="Economi Analyzer API",
    description="AI-Driven Market Insights Dashboard - Sector Rotation Analysis",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(market_router)
app.include_router(news_router)
app.include_router(analysis_router)


@app.get("/")
def root():
    return {
        "name": "Economi Analyzer API",
        "version": "0.1.0",
        "docs": "/docs",
    }
```

> CORS origins에 `http://localhost:5173` 추가 (Vite 기본 포트).
> `create_scheduler` import를 lifespan 내부로 이동하여 테스트 시 불필요한 모듈 로딩 방지.

- [ ] **Step 2: 전체 테스트 실행**

```bash
cd backend && python -m pytest -v
```

Expected: ALL PASSED (기존 34 + 신규 테스트 모두)

- [ ] **Step 3: 커밋**

```bash
git add backend/app/main.py
git commit -m "feat: integrate APScheduler lifespan into FastAPI app"
```

---

## Task 8: 전체 통합 테스트 + 최종 검증

**Files:**
- 전체 테스트 스위트 실행
- API 문서 확인

- [ ] **Step 1: 전체 테스트 실행**

```bash
cd backend && python -m pytest -v --tb=short
```

Expected: ALL PASSED

- [ ] **Step 2: API 문서 확인 (수동)**

```bash
cd backend && python -c "from app.main import app; import json; print(json.dumps([r.path for r in app.routes], indent=2))"
```

Expected output에 다음 경로 포함:
- `/health`
- `/api/market/indices`
- `/api/market/sectors`
- `/api/market/indicators`
- `/api/market/regime`
- `/api/news/articles`
- `/api/news/impacts`
- `/api/analysis/report`
- `/api/analysis/scoreboards`
- `/api/analysis/signals`
- `/api/analysis/trigger`

- [ ] **Step 3: ruff 린트 검사**

```bash
cd backend && python -m ruff check app/ tests/
```

Expected: 에러 없음 (또는 수정 후 재실행)

- [ ] **Step 4: 최종 커밋 (필요 시)**

```bash
git add -A
git commit -m "test: verify Phase 3 API + scheduler integration"
```
