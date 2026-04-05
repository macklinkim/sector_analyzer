# backend/app/models/market.py
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class MarketIndex(BaseModel):
    symbol: str
    name: str
    price: Decimal
    change_percent: Decimal
    collected_at: datetime


class Sector(BaseModel):
    name: str
    etf_symbol: str
    price: Decimal
    change_percent: Decimal
    volume: int
    avg_volume_20d: int | None = None
    volume_change_percent: Decimal | None = None
    relative_strength: Decimal | None = None
    momentum_1w: Decimal | None = None
    momentum_1m: Decimal | None = None
    momentum_3m: Decimal | None = None
    momentum_6m: Decimal | None = None
    momentum_1y: Decimal | None = None
    week_52_low: Decimal | None = None
    week_52_high: Decimal | None = None
    rs_rank: int | None = None
    collected_at: datetime


class EconomicIndicator(BaseModel):
    indicator_name: str
    value: Decimal
    previous_value: Decimal | None = None
    change_direction: str
    source: str
    reported_at: datetime
