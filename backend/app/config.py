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

    # Claude model per analysis type. claude-sonnet-4-20250514 was retired on
    # 2026-06-15 (404 not_found_error), which silently broke the analyst batch;
    # haiku-4-5 keeps token usage minimal and is already proven on news/crisis.
    claude_model_news: str = "claude-haiku-4-5-20251001"
    claude_model_crisis: str = "claude-haiku-4-5-20251001"
    claude_model_analyst: str = "claude-haiku-4-5-20251001"

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

    # Simple auth: comma-separated allowed names (seed fallback — DB `allowed_users` is authoritative)
    allowed_users: str = "admin"
    # Comma-separated names with admin privileges (user management modal)
    admin_users: str = "mack,macklin"

    # Crypto data sources (CryptoCompare news API is keyless; placeholder kept for future paid tier)
    cryptopanic_api_key: str = ""

    # Playwright
    playwright_timeout_sec: int = 30
    playwright_max_instances: int = 2

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
