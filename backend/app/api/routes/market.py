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
