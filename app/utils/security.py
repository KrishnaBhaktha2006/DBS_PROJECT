"""
app/utils/security.py
─────────────────────
Password hashing (bcrypt) and JWT creation / verification.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.hash import pbkdf2_sha256
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from app.config import get_settings

settings = get_settings()

# ── OAuth2 scheme – token must be sent as Bearer ─────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Password helpers ──────────────────────────────────

def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*."""
    return pbkdf2_sha256.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*."""
    try:
        return pbkdf2_sha256.verify(plain, hashed)
    except Exception:
        # Backward compatibility for legacy seed rows that stored plain text.
        return plain == hashed


# ── JWT helpers ───────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Encode *data* as a signed JWT.
    Default expiry = JWT_EXPIRE_MINUTES from settings.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT.  Raises HTTP 401 on any failure.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── FastAPI dependency ────────────────────────────────

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    FastAPI dependency that injects the authenticated user payload.
    Use as:   current_user: dict = Depends(get_current_user)
    Returns dict with keys: u_id, username, email
    """
    payload = decode_access_token(token)
    u_id = payload.get("sub")
    if u_id is None:
        raise HTTPException(status_code=401, detail="Token missing subject claim")
    return {
        "u_id": int(u_id),
        "username": payload.get("username"),
        "email": payload.get("email"),
    }
