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
