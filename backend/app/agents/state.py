from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, TypedDict

from app.models.market import MarketIndex, Sector, EconomicIndicator
from app.models.news import NewsArticle, NewsImpactAnalysis
from app.models.analysis import MacroRegime, SectorScoreboard, RotationSignal, MarketReport


@dataclass
class MarketData:
    indices: list[dict] = field(default_factory=list)
    sectors: list[dict] = field(default_factory=list)
    economic_indicators: list[dict] = field(default_factory=list)
    momentum: dict[str, dict] = field(default_factory=dict)
    relative_strength: dict[str, float] = field(default_factory=dict)


@dataclass
class NewsData:
    articles_by_category: dict[str, list[dict]] = field(default_factory=dict)
    article_summaries: list[dict] = field(default_factory=list)


@dataclass
class AnalysisResults:
    regime: dict | None = None
    scoreboards: list[dict] = field(default_factory=list)
    rotation_signals: list[dict] = field(default_factory=list)
    news_impacts: list[dict] = field(default_factory=list)
    report: dict | None = None


class MarketAnalysisState(TypedDict):
    batch_type: str
    triggered_at: str
    market_data: MarketData | None
    news_data: NewsData | None
    news_fallback_used: bool
    analysis_results: AnalysisResults | None


def create_initial_state(batch_type: str) -> MarketAnalysisState:
    return MarketAnalysisState(
        batch_type=batch_type,
        triggered_at=datetime.now(timezone.utc).isoformat(),
        market_data=None,
        news_data=None,
        news_fallback_used=False,
        analysis_results=None,
    )
