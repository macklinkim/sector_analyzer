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

    # --- 프론트엔드용 조회 메서드 ---

    def get_latest_indices(self) -> list[dict]:
        result = (
            self.client.table("market_indices")
            .select("*")
            .order("collected_at", desc=True)
            .limit(10)
            .execute()
        )
        return result.data

    def get_latest_sectors(self) -> list[dict]:
        result = (
            self.client.table("sectors")
            .select("*")
            .order("collected_at", desc=True)
            .limit(12)
            .execute()
        )
        return result.data

    def get_latest_economic_indicators(self) -> list[dict]:
        result = (
            self.client.table("economic_indicators")
            .select("*")
            .order("reported_at", desc=True)
            .limit(10)
            .execute()
        )
        return result.data

    def get_latest_news_articles(self, limit: int = 20) -> list[dict]:
        result = (
            self.client.table("news_articles")
            .select("*")
            .order("published_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data

    def get_news_by_category(self, category: str, limit: int = 10) -> list[dict]:
        result = (
            self.client.table("news_articles")
            .select("*")
            .eq("category", category)
            .order("published_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data

    def get_latest_news_impacts(self) -> list[dict]:
        result = (
            self.client.table("news_impact_analyses")
            .select("*")
            .order("analyzed_at", desc=True)
            .limit(50)
            .execute()
        )
        return result.data

    def get_latest_report(self) -> dict | None:
        result = (
            self.client.table("market_reports")
            .select("*")
            .order("analyzed_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    def get_latest_rotation_signals(self) -> list[dict]:
        result = (
            self.client.table("rotation_signals")
            .select("*")
            .order("detected_at", desc=True)
            .limit(20)
            .execute()
        )
        return result.data
