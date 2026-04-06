import logging
import time

from supabase import create_client, Client

from app.config import Settings
from app.models.market import MarketIndex, Sector, EconomicIndicator
from app.models.news import NewsArticle

logger = logging.getLogger(__name__)


class SupabaseService:
    def __init__(self, settings: Settings) -> None:
        self._url = settings.supabase_url
        self._key = settings.supabase_service_key
        self.client: Client = create_client(self._url, self._key)

    def _reconnect(self) -> None:
        """Recreate client on connection errors (HTTP/2 termination)."""
        logger.warning("Supabase connection reset — recreating client")
        self.client = create_client(self._url, self._key)

    def _safe_execute(self, fn, retries: int = 2):
        """Execute a Supabase query with retry on connection errors."""
        for attempt in range(retries + 1):
            try:
                return fn()
            except Exception as e:
                err_str = str(e).lower()
                if "connectionterminated" in err_str or "remoteprotocolerror" in err_str or "connection" in err_str:
                    if attempt < retries:
                        logger.warning("Supabase connection error (attempt %d/%d): %s", attempt + 1, retries + 1, e)
                        self._reconnect()
                        time.sleep(0.5)
                        continue
                raise

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
        def _q():
            return (
                self.client.table("macro_regimes")
                .select("*").order("analyzed_at", desc=True).limit(1).execute()
            )
        result = self._safe_execute(_q)
        return result.data[0] if result.data else None

    def get_sector_mapping(self) -> list[dict]:
        def _q():
            return (
                self.client.table("sector_regime_mapping")
                .select("*").order("display_order").execute()
            )
        return self._safe_execute(_q).data

    def get_latest_scoreboards(self, batch_type: str) -> list[dict]:
        def _q():
            return (
                self.client.table("sector_scoreboards")
                .select("*").eq("batch_type", batch_type)
                .order("scored_at", desc=True).limit(12).execute()
            )
        return self._safe_execute(_q).data

    # --- 프론트엔드용 조회 메서드 ---

    def get_latest_indices(self) -> list[dict]:
        def _q():
            return (
                self.client.table("market_indices")
                .select("*").order("collected_at", desc=True).limit(20).execute()
            )
        result = self._safe_execute(_q)
        seen: set[str] = set()
        deduped: list[dict] = []
        for row in result.data:
            sym = row.get("symbol", "")
            if sym not in seen:
                seen.add(sym)
                deduped.append(row)
        return deduped

    def get_latest_sectors(self) -> list[dict]:
        def _q():
            return (
                self.client.table("sectors")
                .select("*").order("collected_at", desc=True).limit(30).execute()
            )
        result = self._safe_execute(_q)
        seen: set[str] = set()
        deduped: list[dict] = []
        for row in result.data:
            sym = row.get("etf_symbol", "")
            if sym not in seen:
                seen.add(sym)
                deduped.append(row)
        return deduped

    def get_latest_economic_indicators(self) -> list[dict]:
        def _q():
            return (
                self.client.table("economic_indicators")
                .select("*").order("reported_at", desc=True).limit(20).execute()
            )
        result = self._safe_execute(_q)
        seen: set[str] = set()
        deduped: list[dict] = []
        for row in result.data:
            name = row.get("indicator_name", "")
            if name not in seen:
                seen.add(name)
                deduped.append(row)
        return deduped

    def get_latest_news_articles(self, limit: int = 20) -> list[dict]:
        def _q():
            return (
                self.client.table("news_articles")
                .select("*").order("published_at", desc=True).limit(limit).execute()
            )
        return self._safe_execute(_q).data

    def get_news_by_category(self, category: str, limit: int = 10) -> list[dict]:
        def _q():
            return (
                self.client.table("news_articles")
                .select("*").eq("category", category)
                .order("published_at", desc=True).limit(limit).execute()
            )
        return self._safe_execute(_q).data

    def get_latest_news_impacts(self) -> list[dict]:
        def _q():
            return (
                self.client.table("news_impact_analyses")
                .select("*").order("analyzed_at", desc=True).limit(50).execute()
            )
        return self._safe_execute(_q).data

    def get_latest_report(self) -> dict | None:
        def _q():
            return (
                self.client.table("market_reports")
                .select("*").order("analyzed_at", desc=True).limit(1).execute()
            )
        result = self._safe_execute(_q)
        return result.data[0] if result.data else None

    def get_latest_rotation_signals(self) -> list[dict]:
        def _q():
            return (
                self.client.table("rotation_signals")
                .select("*").order("detected_at", desc=True).limit(20).execute()
            )
        return self._safe_execute(_q).data
