from functools import lru_cache
from typing import Annotated, Literal

import jwt
from fastapi import Depends, Header, HTTPException, status
from jwt import PyJWKClient
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


@lru_cache
def _get_jwks_client(jwks_url: str) -> PyJWKClient:
    """Cache one JWKS client per URL. Keys are fetched and cached on first use."""
    return PyJWKClient(jwks_url, cache_keys=True, lifespan=3600)


class CurrentUser(BaseModel):
    """Authenticated identity. Either a legacy name user or a Supabase email user."""

    identity: str  # name (legacy) or email (supabase)
    source: Literal["legacy", "supabase"]
    is_admin: bool = False
    photo_url: str | None = None


def _is_admin_name(name: str, settings: Settings) -> bool:
    admins = {n.strip().lower() for n in settings.admin_users.split(",") if n.strip()}
    return name.strip().lower() in admins


# Supabase GoTrue accepts both the new asymmetric signing keys (ES256 via JWKS)
# and the legacy shared HS256 secret. Try JWKS first, fall back to the legacy
# secret if present — this lets the deployment roll forward without coupling to
# either scheme exclusively.
_SUPABASE_JWT_ALGORITHMS = ["ES256", "RS256", "HS256"]


def _decode_supabase_jwt(token: str, settings: Settings) -> dict | None:
    # JWKS path: works for new asymmetric signing keys. No env secret needed.
    jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    try:
        jwks_client = _get_jwks_client(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=_SUPABASE_JWT_ALGORITHMS,
            audience="authenticated",
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError:
        pass
    except Exception:
        # Network errors on JWKS fetch, malformed JWKS, etc. — fall through to legacy.
        pass

    if settings.supabase_jwt_secret:
        try:
            return jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
                options={"require": ["exp", "sub"]},
            )
        except jwt.PyJWTError:
            return None
    return None


def get_current_user(
    settings: Annotated[Settings, Depends(get_settings)],
    supabase: Annotated[SupabaseService, Depends(get_supabase)],
    authorization: Annotated[str | None, Header()] = None,
) -> CurrentUser:
    """Resolve the caller from either a Supabase JWT or a legacy session token.

    Header format: ``Authorization: Bearer <token>``.
    - Supabase JWT: verified against the project's JWKS (ES256) with a legacy
      ``SUPABASE_JWT_SECRET`` fallback. Email must appear in ``allowed_emails``.
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

    # Supabase JWT first (three dot-separated base64 segments)
    if token.count(".") == 2:
        payload = _decode_supabase_jwt(token, settings)
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
        user_row = supabase.get_allowed_user(name)
        return CurrentUser(
            identity=name,
            source="legacy",
            is_admin=_is_admin_name(name, settings),
            photo_url=user_row.get("photo_url") if user_row else None,
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 세션입니다",
    )


def require_admin(
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    """Gate an endpoint to admin users only (legacy admin names)."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다",
        )
    return user
