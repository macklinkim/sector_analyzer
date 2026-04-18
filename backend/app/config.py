from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    anthropic_api_key: str
    eodhd_api_key: str
    newsapi_key: str

    # Supabase
    supabase_url: str
    supabase_service_key: str
    # Supabase Auth JWT secret (Dashboard → Settings → API → JWT Secret)
    supabase_jwt_secret: str = ""

    # Claude model per analysis type — cheaper models for simple classification,
    # reserve the stronger model for the analyst's multi-factor reasoning.
    claude_model_news: str = "claude-haiku-4-5-20251001"
    claude_model_crisis: str = "claude-haiku-4-5-20251001"
    claude_model_analyst: str = "claude-sonnet-4-20250514"

    # Scheduler
    pre_market_time: str = "08:30"
    post_market_time: str = "17:00"
    timezone: str = "US/Eastern"

    # NewsAPI
    newsapi_daily_limit: int = 100
    newsapi_categories: list[str] = ["business", "technology", "science", "general"]

    # EODHD
    eodhd_base_url: str = "https://eodhd.com/api"

    # Trigger API Key (manual pipeline trigger protection)
    trigger_api_key: str = ""

    # CORS: comma-separated allowed origins (added to defaults)
    cors_origins: str = ""

    # Simple auth: comma-separated allowed names
    allowed_users: str = "admin"

    # Playwright
    playwright_timeout_sec: int = 30
    playwright_max_instances: int = 2

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
