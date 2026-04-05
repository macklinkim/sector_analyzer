from unittest.mock import MagicMock
from app.services.supabase import SupabaseService


def _make_service(mock_client: MagicMock) -> SupabaseService:
    svc = object.__new__(SupabaseService)
    svc.client = mock_client
    return svc


def test_get_latest_indices(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"symbol": "SPY", "name": "S&P 500", "price": "500.0", "change_percent": "0.5"}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_indices()
    assert len(result) == 1
    assert result[0]["symbol"] == "SPY"
    mock_supabase_client.table.assert_called_with("market_indices")


def test_get_latest_sectors(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"name": "Technology", "etf_symbol": "XLK", "change_percent": "1.2"}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_sectors()
    assert len(result) == 1
    assert result[0]["name"] == "Technology"


def test_get_latest_economic_indicators(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"indicator_name": "US10Y", "value": "4.25"}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_economic_indicators()
    assert len(result) == 1


def test_get_latest_news_articles(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"title": "Fed holds rates", "category": "business"}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_news_articles(limit=20)
    assert len(result) == 1


def test_get_news_by_category(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"title": "Tech earnings", "category": "business"}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_news_by_category("business", limit=10)
    assert len(result) == 1


def test_get_latest_news_impacts(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"sector_name": "Technology", "impact_score": 7.5}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_news_impacts()
    assert len(result) == 1


def test_get_latest_report(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"batch_type": "pre_market", "summary": "Bullish outlook"}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_report()
    assert result is not None
    assert result["summary"] == "Bullish outlook"


def test_get_latest_report_empty(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = []
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_report()
    assert result is None


def test_get_latest_rotation_signals(mock_supabase_client):
    mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"signal_type": "rotate_in", "to_sector": "Technology"}
    ]
    svc = _make_service(mock_supabase_client)
    result = svc.get_latest_rotation_signals()
    assert len(result) == 1
