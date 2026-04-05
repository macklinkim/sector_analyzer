from functools import lru_cache
from app.config import Settings
from app.services.supabase import SupabaseService


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_supabase() -> SupabaseService:
    settings = get_settings()
    return SupabaseService(settings)
