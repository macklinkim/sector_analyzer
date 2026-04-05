import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.agents.graph import build_graph
from app.agents.state import create_initial_state
from app.api.deps import get_settings, get_supabase
from app.config import Settings
from app.services.supabase import SupabaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


def run_pipeline(batch_type: str = "manual") -> dict:
    graph = build_graph()
    initial_state = create_initial_state(batch_type)
    graph.invoke(initial_state)
    return {"status": "completed", "batch_type": batch_type}


@router.get("/report")
def get_report(svc: SupabaseService = Depends(get_supabase)):
    report = svc.get_latest_report()
    if report is None:
        raise HTTPException(status_code=404, detail="No report available")
    return report


@router.get("/scoreboards")
def get_scoreboards(
    batch_type: str = Query("pre_market", description="Batch type: pre_market or post_market"),
    svc: SupabaseService = Depends(get_supabase),
):
    return svc.get_latest_scoreboards(batch_type)


@router.get("/signals")
def get_rotation_signals(svc: SupabaseService = Depends(get_supabase)):
    return svc.get_latest_rotation_signals()


@router.post("/trigger")
def trigger_pipeline(
    x_api_key: str = Header(..., alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
):
    if not settings.trigger_api_key or x_api_key != settings.trigger_api_key:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        result = run_pipeline("manual")
        return result
    except Exception as e:
        logger.exception("Pipeline trigger failed")
        raise HTTPException(status_code=500, detail="Pipeline execution failed")
