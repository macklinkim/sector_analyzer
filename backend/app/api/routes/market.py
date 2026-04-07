import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_supabase
from app.services.supabase import SupabaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/indices")
def get_indices(svc: SupabaseService = Depends(get_supabase)):
    return svc.get_latest_indices()


@router.get("/sectors")
def get_sectors(svc: SupabaseService = Depends(get_supabase)):
    return svc.get_latest_sectors()


@router.get("/indicators")
def get_economic_indicators(svc: SupabaseService = Depends(get_supabase)):
    return svc.get_latest_economic_indicators()


@router.get("/regime")
def get_regime(svc: SupabaseService = Depends(get_supabase)):
    regime = svc.get_latest_regime()
    if regime is None:
        raise HTTPException(status_code=404, detail="No regime data available")
    return regime


@router.get("/sector-history/{etf_symbol}")
def get_sector_history(
    etf_symbol: str,
    days: int = 30,
    svc: SupabaseService = Depends(get_supabase),
):
    """Get historical price data for sparkline charts (from DB)."""
    rows = svc.get_sector_history(etf_symbol, days)
    return [{"date": r["trade_date"], "close": float(r["close"])} for r in reversed(rows)]


@router.get("/sectors-with-history")
def get_sectors_with_history(
    days: int = 30,
    svc: SupabaseService = Depends(get_supabase),
):
    """Get all sectors with bundled price history for sparklines (from DB)."""
    from app.services.yahoo_finance import SECTOR_ETFS

    sectors = svc.get_latest_sectors()
    all_history = svc.get_all_sector_history(days)

    sector_map: dict[str, dict] = {}
    for s in sectors:
        sector_map[s.get("etf_symbol", "")] = s

    # Group history by etf_symbol
    history_map: dict[str, list[dict]] = {}
    for row in all_history:
        sym = row["etf_symbol"]
        if sym not in history_map:
            history_map[sym] = []
        history_map[sym].append({"date": row["trade_date"], "close": float(row["close"])})

    results = []
    for name, symbol in SECTOR_ETFS:
        sector_data = sector_map.get(symbol, {})
        hist = history_map.get(symbol, [])
        # Sort by date ascending
        hist.sort(key=lambda x: x["date"])
        results.append({
            "sector": symbol,
            "name": name,
            "change_percent": sector_data.get("change_percent", 0),
            "price": sector_data.get("price", 0),
            "history": hist[-days:],
        })

    return results


@router.get("/sector-stocks/{etf_symbol}")
def get_sector_stocks(
    etf_symbol: str,
    svc: SupabaseService = Depends(get_supabase),
):
    """Get sector constituent stocks (from DB)."""
    etf_key = etf_symbol.upper()
    rows = svc.get_sector_stocks(etf_key)

    if not rows:
        raise HTTPException(status_code=404, detail=f"No stock data for {etf_symbol}. Run pipeline first.")

    # Add "etc" entry for remaining constituents
    from app.services.sector_stocks import SECTOR_CONSTITUENTS
    total = len(SECTOR_CONSTITUENTS.get(etf_key, []))
    remaining = total - len(rows)
    if remaining > 0:
        rows.append({
            "symbol": "ETC",
            "name": f"기타 ({remaining}종목)",
            "close": 0,
            "change_p": 0,
            "volume": 0,
            "market_cap": 0,
        })

    return rows
