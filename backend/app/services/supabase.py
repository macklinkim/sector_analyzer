from supabase import create_client, Client

from app.config import Settings
from app.models.market import MarketIndex, Sector, EconomicIndicator
from app.models.news import NewsArticle


class SupabaseService:
    def __init__(self, settings: Settings) -> None:
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key,
        )

    def insert_market_index(self, index: MarketIndex) -> dict:
        return (
            self.client.table("market_indices")
            .insert(index.model_dump(mode="json"))
            .execute()
        )

    def insert_sector(self, sector: Sector) -> dict:
        return (
            self.client.table("sectors")
            .insert(sector.model_dump(mode="json"))
            .execute()
        )

    def insert_news_article(self, article: NewsArticle) -> dict:
        return (
            self.client.table("news_articles")
            .upsert(article.model_dump(mode="json"), on_conflict="url")
            .execute()
        )

    def insert_economic_indicator(self, indicator: EconomicIndicator) -> dict:
        return (
            self.client.table("economic_indicators")
            .insert(indicator.model_dump(mode="json"))
            .execute()
        )

    def get_latest_regime(self) -> dict | None:
        result = (
            self.client.table("macro_regimes")
            .select("*")
            .order("analyzed_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    def get_sector_mapping(self) -> list[dict]:
        result = (
            self.client.table("sector_regime_mapping")
            .select("*")
            .order("display_order")
            .execute()
        )
        return result.data

    def get_latest_scoreboards(self, batch_type: str) -> list[dict]:
        result = (
            self.client.table("sector_scoreboards")
            .select("*")
            .eq("batch_type", batch_type)
            .order("scored_at", desc=True)
            .limit(12)
            .execute()
        )
        return result.data
