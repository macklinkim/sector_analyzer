# backend/tests/agents/test_data_agent.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_eodhd_service():
    service = AsyncMock()
    service.fetch_indices.return_value = [
        {"symbol": "SPY", "name": "S&P 500", "close": 5200.50, "change_p": 0.55},
    ]
    service.fetch_sector_etfs.return_value = [
        {"symbol": "XLK", "name": "Technology", "close": 210.30, "change_p": 1.2, "volume": 50000000},
    ]
    service.calculate_momentum.return_value = {
        "momentum_1w": 2.1, "momentum_1m": 5.3, "momentum_3m": 12.0, "momentum_6m": 18.5,
    }
    service.close = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_data_agent_collects_market_data(mock_eodhd_service):
    from app.agents.data_agent import data_agent_node
    from app.agents.state import create_initial_state

    state = create_initial_state("pre_market")

    with patch("app.agents.data_agent.EODHDService", return_value=mock_eodhd_service):
        result = await data_agent_node(state, MagicMock())
        assert result["market_data"] is not None
        assert len(result["market_data"].indices) > 0
        assert len(result["market_data"].sectors) > 0


@pytest.mark.asyncio
async def test_data_agent_calculates_momentum(mock_eodhd_service):
    from app.agents.data_agent import data_agent_node
    from app.agents.state import create_initial_state

    state = create_initial_state("post_market")

    with patch("app.agents.data_agent.EODHDService", return_value=mock_eodhd_service):
        result = await data_agent_node(state, MagicMock())
        assert len(result["market_data"].momentum) > 0
