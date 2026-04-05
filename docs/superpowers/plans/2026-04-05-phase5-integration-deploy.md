# Phase 5: Integration + Deployment

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FastAPI가 프론트엔드 SPA 정적 파일을 서빙하도록 통합, E2E API 통합 테스트 추가, Docker + Railway/Render 배포 설정 완성.

**Architecture:** FastAPI `StaticFiles` + SPA fallback으로 `frontend/dist/`를 서빙. 단일 컨테이너 배포 (빌드 시 npm build → uvicorn 실행). E2E 테스트는 TestClient로 API 엔드포인트 + 정적 파일 서빙을 통합 검증.

**Tech Stack:** FastAPI (StaticFiles), Docker, pytest, uvicorn

**Spec:** `docs/superpowers/specs/2026-04-05-market-insights-dashboard-design.md` (Section 8 Phase 5)

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `backend/app/main.py` | 정적 파일 서빙 + SPA fallback |
| Create | `backend/tests/test_integration.py` | E2E API 통합 테스트 |
| Create | `Dockerfile` | 프로젝트 루트 단일 컨테이너 빌드 |
| Create | `.dockerignore` | Docker 빌드 제외 패턴 |
| Create | `railway.toml` | Railway 배포 설정 (선택) |
| Modify | `backend/pyproject.toml` | aiofiles 의존성 추가 (StaticFiles) |

---

## Task 1: FastAPI 정적 파일 서빙 + SPA Fallback

**Files:**
- Modify: `backend/app/main.py`
- Modify: `backend/pyproject.toml`

- [ ] **Step 1: aiofiles 의존성 추가**

`backend/pyproject.toml`의 `dependencies`에 추가:
```toml
    "aiofiles>=24.0.0",
```

설치:
```bash
cd backend && .venv/Scripts/pip3.exe install -e ".[dev]"
```

- [ ] **Step 2: main.py에 정적 파일 서빙 추가**

`backend/app/main.py`를 수정. 기존 import/router 유지, 파일 하단에 정적 파일 마운트 추가:

기존 `@app.get("/")` root 엔드포인트를 제거하고, 다음을 파일 끝에 추가:

```python
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Static files: serve frontend build
_frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if _frontend_dist.is_dir():
    app.mount("/assets", StaticFiles(directory=_frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        """SPA fallback: serve index.html for all non-API routes."""
        file_path = _frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(_frontend_dist / "index.html")
else:
    @app.get("/")
    def root():
        return {
            "name": "Economi Analyzer API",
            "version": "0.1.0",
            "docs": "/docs",
            "note": "Frontend not built. Run: cd frontend && npm run build",
        }
```

> **핵심**: API 라우터(`/api/*`, `/health`, `/docs`)는 `include_router`로 먼저 등록되어 우선 매칭. `/{full_path:path}`는 catch-all로 SPA fallback.

- [ ] **Step 3: 프론트엔드 빌드 확인**

```bash
cd frontend && npm run build
```

- [ ] **Step 4: 통합 동작 확인 (수동)**

```bash
cd backend && .venv/Scripts/python.exe -m uvicorn app.main:app --port 8000
```

브라우저에서:
- `http://localhost:8000/api/market/indices` → JSON 응답
- `http://localhost:8000/health` → 헬스체크 JSON
- `http://localhost:8000/` → SPA index.html 서빙
- `http://localhost:8000/docs` → Swagger UI

- [ ] **Step 5: 커밋**

```bash
git add backend/pyproject.toml backend/app/main.py
git commit -m "feat: serve frontend SPA static files from FastAPI with fallback"
```

---

## Task 2: E2E 통합 테스트

**Files:**
- Create: `backend/tests/test_integration.py`

- [ ] **Step 1: 통합 테스트 작성**

```python
# backend/tests/test_integration.py
"""E2E integration tests — verifies API endpoints return expected shapes
and static file serving works when frontend is built."""
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(mock_settings):
    from app.api.deps import get_settings, get_supabase
    from app.main import app

    mock_svc = MagicMock()
    mock_svc.get_latest_indices.return_value = [
        {"symbol": "SPY", "name": "S&P 500", "price": "500.0", "change_percent": "0.5", "collected_at": "2026-04-05T12:00:00Z"}
    ]
    mock_svc.get_latest_sectors.return_value = [
        {"name": "Technology", "etf_symbol": "XLK", "price": "200.0", "change_percent": "1.2", "volume": 1000000, "collected_at": "2026-04-05T12:00:00Z"}
    ]
    mock_svc.get_latest_economic_indicators.return_value = [
        {"indicator_name": "US10Y", "value": "4.25", "change_direction": "up", "source": "EODHD", "reported_at": "2026-04-05T12:00:00Z"}
    ]
    mock_svc.get_latest_regime.return_value = {
        "regime": "goldilocks", "growth_direction": "high", "inflation_direction": "low",
        "regime_probabilities": {"goldilocks": 0.6}, "reasoning": "test", "batch_type": "pre_market", "analyzed_at": "2026-04-05T12:00:00Z"
    }
    mock_svc.get_latest_news_articles.return_value = []
    mock_svc.get_news_by_category.return_value = []
    mock_svc.get_latest_news_impacts.return_value = []
    mock_svc.get_latest_report.return_value = None
    mock_svc.get_latest_scoreboards.return_value = []
    mock_svc.get_latest_rotation_signals.return_value = []

    app.dependency_overrides[get_settings] = lambda: mock_settings
    app.dependency_overrides[get_supabase] = lambda: mock_svc
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestHealthAndDocs:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_openapi_docs(self, client):
        resp = client.get("/docs")
        assert resp.status_code == 200
        assert "swagger" in resp.text.lower() or "openapi" in resp.text.lower()


class TestMarketEndpoints:
    def test_indices(self, client):
        resp = client.get("/api/market/indices")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "symbol" in data[0]

    def test_sectors(self, client):
        resp = client.get("/api/market/sectors")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_indicators(self, client):
        resp = client.get("/api/market/indicators")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_regime(self, client):
        resp = client.get("/api/market/regime")
        assert resp.status_code == 200
        data = resp.json()
        assert data["regime"] in ["goldilocks", "reflation", "stagflation", "deflation"]


class TestNewsEndpoints:
    def test_articles(self, client):
        resp = client.get("/api/news/articles")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_articles_with_category(self, client):
        resp = client.get("/api/news/articles?category=business&limit=5")
        assert resp.status_code == 200

    def test_impacts(self, client):
        resp = client.get("/api/news/impacts")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestAnalysisEndpoints:
    def test_report_404(self, client):
        resp = client.get("/api/analysis/report")
        assert resp.status_code == 404

    def test_scoreboards(self, client):
        resp = client.get("/api/analysis/scoreboards?batch_type=pre_market")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_signals(self, client):
        resp = client.get("/api/analysis/signals")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_trigger_requires_api_key(self, client):
        resp = client.post("/api/analysis/trigger")
        assert resp.status_code == 422


class TestStaticFiles:
    def test_spa_index_served(self, client):
        frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
        if not frontend_dist.is_dir():
            pytest.skip("Frontend not built")
        resp = client.get("/")
        assert resp.status_code == 200
        assert "<!doctype html>" in resp.text.lower() or "<!DOCTYPE html>" in resp.text

    def test_spa_fallback_for_unknown_path(self, client):
        frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
        if not frontend_dist.is_dir():
            pytest.skip("Frontend not built")
        resp = client.get("/some/random/path")
        assert resp.status_code == 200
        assert "html" in resp.text.lower()
```

- [ ] **Step 2: 테스트 실행**

```bash
cd backend && .venv/Scripts/python.exe -m pytest tests/test_integration.py -v
```

Expected: ALL PASSED

- [ ] **Step 3: 전체 테스트 스위트 실행**

```bash
cd backend && .venv/Scripts/python.exe -m pytest -v
```

Expected: 기존 62 + 신규 통합 테스트 ALL PASSED

- [ ] **Step 4: 커밋**

```bash
git add backend/tests/test_integration.py
git commit -m "test: add E2E integration tests for all API endpoints + SPA serving"
```

---

## Task 3: Dockerfile (단일 컨테이너)

**Files:**
- Create: `Dockerfile` (프로젝트 루트)
- Create: `.dockerignore`

- [ ] **Step 1: .dockerignore 작성**

```
# .dockerignore
__pycache__
*.pyc
.venv
node_modules
.git
.env
*.md
docs/
backend/tests/
frontend/node_modules/
```

- [ ] **Step 2: Dockerfile 작성**

```dockerfile
# Dockerfile
# Stage 1: Build frontend
FROM node:22-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend + serve static
FROM python:3.12-slim AS runtime
WORKDIR /app

# Install backend dependencies
COPY backend/pyproject.toml backend/
RUN pip install --no-cache-dir -e backend/

# Copy backend source
COPY backend/app/ backend/app/

# Copy frontend build output
COPY --from=frontend-build /app/frontend/dist/ frontend/dist/

# Environment
ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

> 단일 worker (APScheduler는 in-process background thread — 여러 worker에서 중복 실행 방지)

- [ ] **Step 3: Docker 빌드 테스트 (선택 — Docker 있는 경우만)**

```bash
cd C:/Users/mack/Desktop/projects/study/economi_analyzer
docker build -t economi-analyzer .
```

> Docker가 없으면 skip

- [ ] **Step 4: 커밋**

```bash
git add Dockerfile .dockerignore
git commit -m "feat: add Dockerfile for single-container deployment (frontend + backend)"
```

---

## Task 4: Railway/Render 배포 설정

**Files:**
- Create: `railway.toml` (Railway용)
- Create: `render.yaml` (Render용)

- [ ] **Step 1: railway.toml 작성**

```toml
# railway.toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

- [ ] **Step 2: render.yaml 작성**

```yaml
# render.yaml
services:
  - type: web
    name: economi-analyzer
    runtime: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: EODHD_API_KEY
        sync: false
      - key: NEWSAPI_KEY
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: TRIGGER_API_KEY
        sync: false
    healthCheckPath: /health
```

- [ ] **Step 3: 커밋**

```bash
git add railway.toml render.yaml
git commit -m "feat: add Railway + Render deployment configurations"
```

---

## Task 5: 최종 검증

- [ ] **Step 1: 전체 백엔드 테스트**

```bash
cd backend && .venv/Scripts/python.exe -m pytest -v --tb=short
```

Expected: ALL PASSED

- [ ] **Step 2: 프론트엔드 빌드**

```bash
cd frontend && npx tsc --noEmit && npm run build
```

Expected: 에러 없음

- [ ] **Step 3: ruff 린트**

```bash
cd backend && .venv/Scripts/python.exe -m ruff check app/ tests/
```

Expected: Phase 5 파일에 에러 없음

- [ ] **Step 4: 최종 커밋**

```bash
git add -A && git commit -m "chore: Phase 5 integration + deployment complete"
```
