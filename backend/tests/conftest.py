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
    client.table.return_value.insert.return_value.execute = MagicMock(
        return_value=MagicMock(data=[{"id": "test-uuid"}])
    )
    client.table.return_value.upsert.return_value.execute = MagicMock(
        return_value=MagicMock(data=[{"id": "test-uuid"}])
    )
    client.table.return_value.select.return_value.order.return_value.limit.return_value.execute = MagicMock(
        return_value=MagicMock(data=[])
    )
    client.table.return_value.select.return_value.order.return_value.execute = MagicMock(
        return_value=MagicMock(data=[])
    )
    client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute = MagicMock(
        return_value=MagicMock(data=[])
    )
    return client
