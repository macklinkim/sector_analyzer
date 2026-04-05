from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    anthropic_api_key: str
    eodhd_api_key: str
    newsapi_key: str

    # Supabase
    supabase_url: str
    supabase_service_key: str

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

    # Simple auth: comma-separated allowed names
    allowed_users: str = "admin"

    # Playwright
    playwright_timeout_sec: int = 30
    playwright_max_instances: int = 2

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
