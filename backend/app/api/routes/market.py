import logging
import time

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
async def get_sector_history(etf_symbol: str, days: int = 30):
    """Get historical price data for sparkline charts."""
    from app.services.yahoo_finance import YahooFinanceService

    service = YahooFinanceService()
    try:
        history = await service.fetch_historical(etf_symbol, limit=days)
        return [{"date": d["date"], "close": d["close"]} for d in reversed(history)]
    finally:
        await service.close()


@router.get("/sectors-with-history")
async def get_sectors_with_history(
    days: int = 30,
    svc: SupabaseService = Depends(get_supabase),
):
    """Get all sectors with bundled price history for sparklines."""
    from app.services.yahoo_finance import SECTOR_ETFS, YahooFinanceService

    sectors = svc.get_latest_sectors()
    service = YahooFinanceService()

    sector_map: dict[str, dict] = {}
    for s in sectors:
        sector_map[s.get("etf_symbol", "")] = s

    results = []
    try:
        for name, symbol in SECTOR_ETFS:
            sector_data = sector_map.get(symbol, {})
            try:
                history = await service.fetch_historical(symbol, limit=days)
                history_points = [
                    {"date": d["date"], "close": d["close"]}
                    for d in reversed(history)
                ]
            except Exception:
                history_points = []

            results.append({
                "sector": symbol,
                "name": name,
                "change_percent": sector_data.get("change_percent", 0),
                "price": sector_data.get("price", 0),
                "history": history_points,
            })
    finally:
        await service.close()

    return results


# --- Sector Stocks with in-memory cache ---

_sector_stocks_cache: dict[str, tuple[float, list[dict]]] = {}
_SECTOR_STOCKS_TTL = 4 * 60 * 60  # 4 hours


@router.get("/sector-stocks/{etf_symbol}")
async def get_sector_stocks(etf_symbol: str):
    from app.services.sector_stocks import SECTOR_CONSTITUENTS
    from app.services.yahoo_finance import YahooFinanceService

    etf_key = etf_symbol.upper()

    # Check in-memory cache
    cached = _sector_stocks_cache.get(etf_key)
    if cached:
        ts, data = cached
        if time.time() - ts < _SECTOR_STOCKS_TTL:
            return data

    symbols = SECTOR_CONSTITUENTS.get(etf_key, [])
    if not symbols:
        raise HTTPException(status_code=404, detail=f"Unknown sector ETF: {etf_symbol}")

    service = YahooFinanceService()
    try:
        results = await service.fetch_sector_stocks(symbols[:15])

        # Add "etc" for remaining
        remaining = len(symbols) - len(results)
        if remaining > 0:
            results.append({
                "symbol": "ETC",
                "name": f"기타 ({remaining}종목)",
                "close": 0,
                "change_p": 0,
                "volume": 0,
                "market_cap": 0,
            })

        # Cache results
        _sector_stocks_cache[etf_key] = (time.time(), results)
    except Exception as e:
        logger.error("Failed to fetch sector stocks for %s: %s", etf_key, e)
        results = []
    finally:
        await service.close()

    return results
