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
