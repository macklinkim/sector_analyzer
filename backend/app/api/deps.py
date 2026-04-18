from functools import lru_cache
from typing import Annotated, Literal

import jwt
from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel

from app.config import Settings
from app.services.supabase import SupabaseService


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_supabase() -> SupabaseService:
    settings = get_settings()
    return SupabaseService(settings)


class CurrentUser(BaseModel):
    """Authenticated identity. Either a legacy name user or a Supabase email user."""

    identity: str  # name (legacy) or email (supabase)
    source: Literal["legacy", "supabase"]


def _decode_supabase_jwt(token: str, secret: str) -> dict:
    try:
        return jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience="authenticated",
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Supabase token: {e}",
        )


def get_current_user(
    settings: Annotated[Settings, Depends(get_settings)],
    supabase: Annotated[SupabaseService, Depends(get_supabase)],
    authorization: Annotated[str | None, Header()] = None,
) -> CurrentUser:
    """Resolve the caller from either a Supabase JWT or a legacy session token.

    Header format: ``Authorization: Bearer <token>``.
    - Supabase JWT: verified with ``SUPABASE_JWT_SECRET``; email must appear in ``allowed_emails``.
    - Legacy token: looked up in the in-memory session store from ``auth.py``.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty bearer token",
        )

    # Try Supabase JWT first (looks like three dot-separated base64 segments)
    if settings.supabase_jwt_secret and token.count(".") == 2:
        try:
            payload = _decode_supabase_jwt(token, settings.supabase_jwt_secret)
        except HTTPException:
            payload = None
        if payload is not None:
            email = (payload.get("email") or "").lower()
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Supabase token missing email claim",
                )
            if not supabase.is_email_allowed(email):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="승인되지 않은 이메일입니다",
                )
            return CurrentUser(identity=email, source="supabase")

    # Legacy token fallback (in-memory store managed by auth router)
    from app.api.routes.auth import _sessions  # noqa: PLC0415 — avoids circular import

    name = _sessions.get(token)
    if name:
        return CurrentUser(identity=name, source="legacy")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 세션입니다",
    )
