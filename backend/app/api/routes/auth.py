import hashlib
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, EmailStr

from app.api.deps import (
    CurrentUser,
    _is_admin_name,
    get_current_user,
    get_settings,
    get_supabase,
    require_admin,
)
from app.config import Settings
from app.services.supabase import SupabaseService

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Simple in-memory session store for legacy name-only auth (resets on server restart).
# Supabase-authenticated users are identified by their signed JWT — no server state needed.
_sessions: dict[str, str] = {}

ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_AVATAR_BYTES = 2 * 1024 * 1024  # 2 MB


class LoginRequest(BaseModel):
    name: str


class LoginResponse(BaseModel):
    token: str
    name: str
    is_admin: bool
    photo_url: str | None = None


class EmailCheckRequest(BaseModel):
    email: EmailStr


class EmailCheckResponse(BaseModel):
    allowed: bool


class AllowedUserOut(BaseModel):
    name: str
    photo_url: str | None = None
    added_by: str | None = None
    added_at: str | None = None


class AddUserRequest(BaseModel):
    name: str


def _resolve_allowed(name: str, supabase: SupabaseService, settings: Settings) -> bool:
    """DB first, fall back to comma-separated env whitelist for bootstrap."""
    normalized = name.strip().lower()
    if not normalized:
        return False
    if supabase.is_name_allowed(normalized):
        return True
    seed = {n.strip().lower() for n in settings.allowed_users.split(",") if n.strip()}
    return normalized in seed


@router.post("/login", response_model=LoginResponse)
def login(
    req: LoginRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    supabase: Annotated[SupabaseService, Depends(get_supabase)],
) -> LoginResponse:
    """Legacy name-only login. Whitelist lives in the ``allowed_users`` table
    (env ``ALLOWED_USERS`` is honored as a bootstrap seed)."""
    normalized = req.name.strip().lower()
    if not _resolve_allowed(normalized, supabase, settings):
        raise HTTPException(status_code=403, detail="승인되지 않은 사용자입니다")

    token = hashlib.sha256(secrets.token_bytes(32)).hexdigest()[:32]
    _sessions[token] = normalized

    user_row = supabase.get_allowed_user(normalized)
    return LoginResponse(
        token=token,
        name=normalized,
        is_admin=_is_admin_name(normalized, settings),
        photo_url=user_row.get("photo_url") if user_row else None,
    )


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


# --- Admin: manage the dynamic name whitelist ---


@router.get("/allowed-users", response_model=list[AllowedUserOut])
def list_allowed_users(
    _admin: Annotated[CurrentUser, Depends(require_admin)],
    supabase: Annotated[SupabaseService, Depends(get_supabase)],
) -> list[AllowedUserOut]:
    rows = supabase.list_allowed_users()
    return [AllowedUserOut(**row) for row in rows]


@router.post("/allowed-users", response_model=AllowedUserOut, status_code=201)
def add_allowed_user(
    req: AddUserRequest,
    admin: Annotated[CurrentUser, Depends(require_admin)],
    supabase: Annotated[SupabaseService, Depends(get_supabase)],
) -> AllowedUserOut:
    name = req.name.strip().lower()
    if not name:
        raise HTTPException(status_code=400, detail="이름이 비어있습니다")
    row = supabase.upsert_allowed_user(name=name, added_by=admin.identity)
    return AllowedUserOut(**row)


@router.delete("/allowed-users/{name}", status_code=204)
def delete_allowed_user(
    name: str,
    admin: Annotated[CurrentUser, Depends(require_admin)],
    supabase: Annotated[SupabaseService, Depends(get_supabase)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    normalized = name.strip().lower()
    if normalized == admin.identity.strip().lower():
        raise HTTPException(status_code=400, detail="본인 계정은 삭제할 수 없습니다")
    if _is_admin_name(normalized, settings):
        raise HTTPException(status_code=400, detail="관리자 계정은 삭제할 수 없습니다")
    supabase.delete_allowed_user(normalized)


@router.post("/allowed-users/{name}/avatar", response_model=AllowedUserOut)
async def upload_user_avatar(
    name: str,
    admin: Annotated[CurrentUser, Depends(require_admin)],
    supabase: Annotated[SupabaseService, Depends(get_supabase)],
    file: UploadFile = File(...),
) -> AllowedUserOut:
    normalized = name.strip().lower()
    if not supabase.is_name_allowed(normalized):
        raise HTTPException(status_code=404, detail="등록되지 않은 사용자입니다")

    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(status_code=415, detail="jpg/png/webp 만 업로드 가능합니다")

    data = await file.read()
    if len(data) > MAX_AVATAR_BYTES:
        raise HTTPException(status_code=413, detail="2MB 이하의 파일만 업로드 가능합니다")
    if not data:
        raise HTTPException(status_code=400, detail="빈 파일입니다")

    public_url = supabase.upload_avatar(normalized, data, content_type)
    # Append cache-buster so the frontend picks up the new file immediately after re-upload.
    photo_url = f"{public_url}?v={secrets.token_hex(4)}"
    row = supabase.update_allowed_user_photo(normalized, photo_url)
    if row is None:
        # Should not happen (we checked is_name_allowed above) — surface it clearly.
        raise HTTPException(status_code=500, detail="사용자 사진 업데이트에 실패했습니다")
    _ = admin  # silence unused
    return AllowedUserOut(**row)
