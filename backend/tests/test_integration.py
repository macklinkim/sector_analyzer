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
        assert isinstance(resp.json(), list)

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
        assert "html" in resp.text.lower()

    def test_spa_fallback_for_unknown_path(self, client):
        frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
        if not frontend_dist.is_dir():
            pytest.skip("Frontend not built")
        resp = client.get("/some/random/path")
        assert resp.status_code == 200
        assert "html" in resp.text.lower()
