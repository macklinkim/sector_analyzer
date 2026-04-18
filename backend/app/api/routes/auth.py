import hashlib
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from app.api.deps import CurrentUser, get_current_user, get_settings, get_supabase
from app.config import Settings
from app.services.supabase import SupabaseService

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Simple in-memory session store for legacy name-only auth (resets on server restart).
# Supabase-authenticated users are identified by their signed JWT — no server state needed.
_sessions: dict[str, str] = {}


class LoginRequest(BaseModel):
    name: str


class LoginResponse(BaseModel):
    token: str
    name: str


class EmailCheckRequest(BaseModel):
    email: EmailStr


class EmailCheckResponse(BaseModel):
    allowed: bool


@router.post("/login", response_model=LoginResponse)
def login(
    req: LoginRequest,
    settings: Annotated[Settings, Depends(get_settings)],
) -> LoginResponse:
    """Legacy name-only login. Names listed in ``ALLOWED_USERS`` are issued a session token."""
    allowed = [n.strip().lower() for n in settings.allowed_users.split(",") if n.strip()]
    if req.name.strip().lower() not in allowed:
        raise HTTPException(status_code=403, detail="승인되지 않은 사용자입니다")

    token = hashlib.sha256(secrets.token_bytes(32)).hexdigest()[:32]
    _sessions[token] = req.name.strip()
    return LoginResponse(token=token, name=req.name.strip())


@router.get("/verify")
def verify(token: str) -> dict:
    """Legacy endpoint kept for backward compatibility — validates a name-only session token."""
    name = _sessions.get(token)
    if not name:
        raise HTTPException(status_code=401, detail="유효하지 않은 세션입니다")
    return {"valid": True, "name": name}


@router.get("/me", response_model=CurrentUser)
def me(user: Annotated[CurrentUser, Depends(get_current_user)]) -> CurrentUser:
    """Unified session check — accepts either a legacy token or a Supabase JWT."""
    return user


@router.post("/check-email", response_model=EmailCheckResponse)
def check_email(
    req: EmailCheckRequest,
    supabase: Annotated[SupabaseService, Depends(get_supabase)],
) -> EmailCheckResponse:
    """Pre-flight check so the UI can reject non-whitelisted emails before calling Supabase."""
    return EmailCheckResponse(allowed=supabase.is_email_allowed(req.email))
