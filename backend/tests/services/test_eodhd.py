import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal
import httpx


MOCK_EOD_RESPONSE = {
    "close": 5200.50,
    "change_p": 0.55,
    "volume": 80000000,
}

MOCK_HISTORICAL_RESPONSE = [
    {"date": "2026-04-04", "close": 5200.50, "volume": 80000000},
    {"date": "2026-03-28", "close": 5150.00, "volume": 75000000},
    {"date": "2026-03-05", "close": 5050.00, "volume": 70000000},
    {"date": "2026-01-05", "close": 4900.00, "volume": 65000000},
    {"date": "2025-10-05", "close": 4700.00, "volume": 60000000},
]


@pytest.fixture
def eodhd_service(mock_settings):
    from app.services.eodhd import EODHDService
    return EODHDService(mock_settings)


@pytest.mark.asyncio
async def test_fetch_realtime_quote(eodhd_service):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_EOD_RESPONSE
    mock_response.raise_for_status = MagicMock()

    with patch.object(eodhd_service.client, "get", new_callable=AsyncMock, return_value=mock_response):
        result = await eodhd_service.fetch_realtime_quote("SPY.US")
        assert result["close"] == 5200.50


@pytest.mark.asyncio
async def test_fetch_sector_etfs(eodhd_service):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_EOD_RESPONSE
    mock_response.raise_for_status = MagicMock()

    with patch.object(eodhd_service.client, "get", new_callable=AsyncMock, return_value=mock_response):
        results = await eodhd_service.fetch_sector_etfs()
        assert len(results) > 0
        assert "XLK" in [r["symbol"] for r in results]


@pytest.mark.asyncio
async def test_calculate_momentum(eodhd_service):
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_HISTORICAL_RESPONSE
    mock_response.raise_for_status = MagicMock()

    with patch.object(eodhd_service.client, "get", new_callable=AsyncMock, return_value=mock_response):
        momentum = await eodhd_service.calculate_momentum("XLK.US")
        assert "momentum_1w" in momentum
        assert "momentum_1m" in momentum
        assert "momentum_3m" in momentum
        assert "momentum_6m" in momentum
