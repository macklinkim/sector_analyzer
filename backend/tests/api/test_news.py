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
