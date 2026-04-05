from datetime import datetime, timezone
from decimal import Decimal


def test_market_index_model():
    from app.models.market import MarketIndex
    idx = MarketIndex(
        symbol="SPY",
        name="S&P 500",
        price=Decimal("5200.50"),
        change_percent=Decimal("0.55"),
        collected_at=datetime.now(timezone.utc),
    )
    assert idx.symbol == "SPY"
    assert idx.price == Decimal("5200.50")


def test_sector_model_with_momentum():
    from app.models.market import Sector
    sector = Sector(
        name="Technology",
        etf_symbol="XLK",
        price=Decimal("210.30"),
        change_percent=Decimal("1.2"),
        volume=50_000_000,
        avg_volume_20d=45_000_000,
        volume_change_percent=Decimal("11.1"),
        relative_strength=Decimal("1.05"),
        momentum_1w=Decimal("2.1"),
        momentum_1m=Decimal("5.3"),
        momentum_3m=Decimal("12.0"),
        momentum_6m=Decimal("18.5"),
        rs_rank=1,
        collected_at=datetime.now(timezone.utc),
    )
    assert sector.etf_symbol == "XLK"
    assert sector.rs_rank == 1


def test_economic_indicator_model():
    from app.models.market import EconomicIndicator
    ind = EconomicIndicator(
        indicator_name="fed_rate",
        value=Decimal("5.25"),
        previous_value=Decimal("5.00"),
        change_direction="rising",
        source="EODHD",
        reported_at=datetime.now(timezone.utc),
    )
    assert ind.change_direction == "rising"


def test_news_article_model():
    from app.models.news import NewsArticle
    article = NewsArticle(
        category="business",
        title="Fed Holds Rates Steady",
        source="Reuters",
        url="https://reuters.com/article/1",
        summary="The Federal Reserve held rates...",
        published_at=datetime.now(timezone.utc),
        collected_at=datetime.now(timezone.utc),
    )
    assert article.category == "business"


def test_macro_regime_model():
    from app.models.analysis import MacroRegime
    regime = MacroRegime(
        regime="goldilocks",
        growth_direction="high",
        inflation_direction="low",
        regime_probabilities={
            "goldilocks": 0.60,
            "reflation": 0.25,
            "stagflation": 0.10,
            "deflation": 0.05,
        },
        reasoning="Strong GDP growth with falling CPI",
        batch_type="pre_market",
        analyzed_at=datetime.now(timezone.utc),
    )
    assert regime.regime == "goldilocks"
    assert regime.regime_probabilities["goldilocks"] == 0.60


def test_sector_scoreboard_model():
    from app.models.analysis import SectorScoreboard
    sb = SectorScoreboard(
        sector_name="Technology",
        etf_symbol="XLK",
        base_score=Decimal("0.6"),
        override_score=Decimal("0.1"),
        news_sentiment_score=Decimal("0.3"),
        momentum_score=Decimal("0.2"),
        final_score=Decimal("0.72"),
        rank=1,
        recommendation="overweight",
        reasoning="Goldilocks regime favors tech",
        batch_type="pre_market",
        scored_at=datetime.now(timezone.utc),
    )
    assert sb.recommendation == "overweight"
    assert sb.rank == 1


def test_rotation_signal_model():
    from app.models.analysis import RotationSignal
    sig = RotationSignal(
        signal_type="rotation_in",
        to_sector="Technology",
        strength=Decimal("0.8"),
        final_score=Decimal("0.72"),
        reasoning="Money flowing into tech sector",
        batch_type="pre_market",
        detected_at=datetime.now(timezone.utc),
    )
    assert sig.signal_type == "rotation_in"
