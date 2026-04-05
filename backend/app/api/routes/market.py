from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_supabase
from app.services.supabase import SupabaseService

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
    from app.config import Settings
    from app.services.eodhd import EODHDService

    settings = Settings()
    service = EODHDService(settings)
    try:
        history = await service.fetch_historical(f"{etf_symbol}.US", limit=days)
        return [{"date": d["date"], "close": d["close"]} for d in reversed(history)]
    finally:
        await service.close()


@router.get("/sectors-with-history")
async def get_sectors_with_history(
    days: int = 30,
    svc: SupabaseService = Depends(get_supabase),
):
    """Get all sectors with bundled price history for sparklines."""
    from app.config import Settings
    from app.services.eodhd import EODHDService, SECTOR_ETFS

    sectors = svc.get_latest_sectors()
    settings = Settings()
    service = EODHDService(settings)

    # Build etf_symbol → sector map
    sector_map: dict[str, dict] = {}
    for s in sectors:
        sector_map[s.get("etf_symbol", "")] = s

    results = []
    try:
        for name, symbol in SECTOR_ETFS:
            sector_data = sector_map.get(symbol, {})
            try:
                history = await service.fetch_historical(f"{symbol}.US", limit=days)
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


@router.get("/sector-stocks/{etf_symbol}")
async def get_sector_stocks(etf_symbol: str):
    from app.services.sector_stocks import SECTOR_CONSTITUENTS
    from app.config import Settings
    from app.services.eodhd import EODHDService

    symbols = SECTOR_CONSTITUENTS.get(etf_symbol.upper(), [])
    if not symbols:
        raise HTTPException(status_code=404, detail=f"Unknown sector ETF: {etf_symbol}")

    settings = Settings()
    service = EODHDService(settings)
    results = []
    try:
        for sym in symbols[:15]:
            try:
                quote = await service.fetch_realtime_quote(f"{sym}.US")
                results.append({
                    "symbol": sym,
                    "name": sym,
                    "close": quote.get("close", 0),
                    "change_p": quote.get("change_p", 0),
                    "volume": quote.get("volume", 0),
                    "market_cap": quote.get("volume", 0) * quote.get("close", 1),
                })
            except Exception:
                pass
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
    finally:
        await service.close()

    return results
