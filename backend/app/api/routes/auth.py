import hashlib
import secrets
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_settings
from app.config import Settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Simple in-memory session store (resets on server restart)
_sessions: dict[str, str] = {}


class LoginRequest(BaseModel):
    name: str


class LoginResponse(BaseModel):
    token: str
    name: str


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, settings: Settings = Depends(get_settings)):
    allowed = [n.strip().lower() for n in settings.allowed_users.split(",") if n.strip()]
    if req.name.strip().lower() not in allowed:
        raise HTTPException(status_code=403, detail="승인되지 않은 사용자입니다")

    token = hashlib.sha256(secrets.token_bytes(32)).hexdigest()[:32]
    _sessions[token] = req.name.strip()
    return LoginResponse(token=token, name=req.name.strip())


@router.get("/verify")
def verify(token: str, settings: Settings = Depends(get_settings)):
    name = _sessions.get(token)
    if not name:
        raise HTTPException(status_code=401, detail="유효하지 않은 세션입니다")
    return {"valid": True, "name": name}
