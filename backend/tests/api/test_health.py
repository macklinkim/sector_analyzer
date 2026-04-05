import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(mock_settings):
    from app.api.deps import get_settings
    from app.main import app

    app.dependency_overrides[get_settings] = lambda: mock_settings
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_returns_response(client):
    resp = client.get("/")
    assert resp.status_code == 200
    # Either SPA HTML (frontend built) or JSON info (frontend not built)
    content_type = resp.headers.get("content-type", "")
    if "json" in content_type:
        assert "name" in resp.json()
    else:
        assert "html" in resp.text.lower()
