# backend/tests/agents/test_analyst_agent.py
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch


MOCK_CLAUDE_REGIME_RESPONSE = json.dumps({
    "regime": "goldilocks",
    "growth_direction": "high",
    "inflation_direction": "low",
    "regime_probabilities": {
        "goldilocks": 0.60, "reflation": 0.25, "stagflation": 0.10, "deflation": 0.05
    },
    "reasoning": "Strong GDP growth with controlled inflation"
})

MOCK_CLAUDE_SCORING_RESPONSE = json.dumps({
    "scoreboards": [
        {
            "sector_name": "Technology", "etf_symbol": "XLK",
            "base_score": "0.6", "override_score": "0.1",
            "news_sentiment_score": "0.3", "momentum_score": "0.2",
            "final_score": "0.72", "rank": 1,
            "recommendation": "overweight",
            "reasoning": "Goldilocks favors tech"
        }
    ],
    "rotation_signals": [
        {
            "signal_type": "rotation_in", "to_sector": "Technology",
            "strength": "0.8", "final_score": "0.72",
            "reasoning": "Money flowing into tech"
        }
    ],
    "report_summary": "Market in Goldilocks regime. Tech leads.",
    "key_highlights": ["Strong GDP", "Low inflation", "Tech sector outperforming"]
})


@pytest.fixture
def mock_anthropic_client():
    client = MagicMock()
    regime_msg = MagicMock()
    regime_msg.content = [MagicMock(text=MOCK_CLAUDE_REGIME_RESPONSE)]
    scoring_msg = MagicMock()
    scoring_msg.content = [MagicMock(text=MOCK_CLAUDE_SCORING_RESPONSE)]
    client.messages.create = MagicMock(side_effect=[regime_msg, scoring_msg])
    return client


@pytest.fixture
def mock_supabase_service():
    service = MagicMock()
    service.get_sector_mapping.return_value = [
        {
            "sector_name": "Technology", "etf_symbols": ["XLK"],
            "favorable_regimes": ["goldilocks"], "unfavorable_regimes": ["stagflation"],
            "override_rules": None, "display_order": 3,
        }
    ]
    return service


def _make_state():
    from app.agents.state import create_initial_state, MarketData, NewsData
    state = create_initial_state("pre_market")
    state["market_data"] = MarketData(
        indices=[{"symbol": "SPY", "close": 5200, "change_p": 0.5}],
        sectors=[{"symbol": "XLK", "name": "Technology", "close": 210, "change_p": 1.2, "volume": 50000000}],
        momentum={"XLK": {"momentum_1w": 2.1, "momentum_1m": 5.3, "momentum_3m": 12.0, "momentum_6m": 18.5}},
    )
    state["news_data"] = NewsData(
        articles_by_category={"business": [{"title": "GDP Growth Strong", "description": "Economy growing"}]},
    )
    return state


@pytest.mark.asyncio
async def test_analyst_agent_produces_regime(mock_anthropic_client, mock_supabase_service):
    from app.agents.analyst_agent import analyst_agent_node
    state = _make_state()

    with patch("app.agents.analyst_agent.anthropic.Anthropic", return_value=mock_anthropic_client), \
         patch("app.agents.analyst_agent.SupabaseService", return_value=mock_supabase_service):
        result = await analyst_agent_node(state, MagicMock())
        assert result["analysis_results"] is not None
        assert result["analysis_results"].regime is not None
        assert result["analysis_results"].regime["regime"] == "goldilocks"


@pytest.mark.asyncio
async def test_analyst_agent_produces_scoreboards(mock_anthropic_client, mock_supabase_service):
    from app.agents.analyst_agent import analyst_agent_node
    state = _make_state()

    # Need fresh side_effect since previous test consumed it
    regime_msg = MagicMock()
    regime_msg.content = [MagicMock(text=MOCK_CLAUDE_REGIME_RESPONSE)]
    scoring_msg = MagicMock()
    scoring_msg.content = [MagicMock(text=MOCK_CLAUDE_SCORING_RESPONSE)]
    mock_anthropic_client.messages.create = MagicMock(side_effect=[regime_msg, scoring_msg])

    with patch("app.agents.analyst_agent.anthropic.Anthropic", return_value=mock_anthropic_client), \
         patch("app.agents.analyst_agent.SupabaseService", return_value=mock_supabase_service):
        result = await analyst_agent_node(state, MagicMock())
        assert len(result["analysis_results"].scoreboards) > 0
        assert result["analysis_results"].report is not None
