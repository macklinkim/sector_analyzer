import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from decimal import Decimal


def test_supabase_client_init(mock_settings):
    from app.services.supabase import SupabaseService
    with patch("app.services.supabase.create_client") as mock_create:
        mock_create.return_value = MagicMock()
        service = SupabaseService(mock_settings)
        mock_create.assert_called_once_with(
            mock_settings.supabase_url,
            mock_settings.supabase_service_key,
        )


def test_insert_market_index(mock_settings, mock_supabase_client):
    from app.services.supabase import SupabaseService
    from app.models.market import MarketIndex

    with patch("app.services.supabase.create_client", return_value=mock_supabase_client):
        service = SupabaseService(mock_settings)
        idx = MarketIndex(
            symbol="SPY",
            name="S&P 500",
            price=Decimal("5200.50"),
            change_percent=Decimal("0.55"),
            collected_at=datetime.now(timezone.utc),
        )
        service.insert_market_index(idx)
        mock_supabase_client.table.assert_called_with("market_indices")
