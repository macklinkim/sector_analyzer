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
