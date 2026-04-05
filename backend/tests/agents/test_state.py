from datetime import datetime, timezone


def test_create_initial_state():
    from app.agents.state import create_initial_state
    state = create_initial_state("pre_market")
    assert state["batch_type"] == "pre_market"
    assert state["triggered_at"] is not None
    assert state["market_data"] is None
    assert state["news_data"] is None
    assert state["news_fallback_used"] is False
    assert state["analysis_results"] is None


def test_market_data_structure():
    from app.agents.state import MarketData
    data = MarketData(indices=[], sectors=[], economic_indicators=[], momentum={})
    assert data.indices == []
    assert data.momentum == {}


def test_news_data_structure():
    from app.agents.state import NewsData
    data = NewsData(articles_by_category={}, article_summaries=[])
    assert data.articles_by_category == {}


def test_analysis_results_structure():
    from app.agents.state import AnalysisResults
    results = AnalysisResults(regime=None, scoreboards=[], rotation_signals=[], news_impacts=[], report=None)
    assert results.scoreboards == []
