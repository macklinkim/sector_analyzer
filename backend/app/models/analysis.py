# backend/app/models/analysis.py
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class MacroRegime(BaseModel):
    regime: str
    growth_direction: str
    inflation_direction: str
    transition_from: str | None = None
    transition_probability: float | None = None
    regime_probabilities: dict[str, float]
    indicators_snapshot: dict | None = None
    reasoning: str
    batch_type: str
    analyzed_at: datetime


class SectorScoreboard(BaseModel):
    sector_name: str
    etf_symbol: str
    base_score: Decimal
    override_score: Decimal
    news_sentiment_score: Decimal
    momentum_score: Decimal
    final_score: Decimal
    rank: int
    recommendation: str
    reasoning: str
    batch_type: str
    scored_at: datetime


class RotationSignal(BaseModel):
    signal_type: str  # rotate_in, rotate_out, regime_shift
    signal_grade: str = "WATCH"  # MAJOR, ALERT, WATCH
    from_sector: str | None = None
    to_sector: str | None = None
    strength: Decimal
    base_score: Decimal | None = None
    override_adjustment: Decimal | None = None
    final_score: Decimal
    confidence_score: Decimal = Decimal("0.5")
    macro_environment: str = ""  # Risk-On, Risk-Off, Inflationary, Deflationary
    reasoning: str
    supporting_news_urls: list[str] = []
    batch_type: str
    detected_at: datetime


class MarketReport(BaseModel):
    batch_type: str
    summary: str
    key_highlights: list[str]
    regime: MacroRegime
    top_sectors: list[SectorScoreboard]
    bottom_sectors: list[SectorScoreboard]
    rotation_signals: list[RotationSignal]
    report_date: str
    analyzed_at: datetime
    disclaimer: str = "본 분석은 AI의 추론이며, 실제 투자 판단의 근거로 사용할 수 없습니다."
