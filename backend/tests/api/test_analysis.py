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
