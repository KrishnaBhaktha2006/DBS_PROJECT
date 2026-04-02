"""
app/routes/users.py
────────────────────
GET /users/me          → authenticated user's own profile
GET /users/{u_id}      → any user's public profile
"""

from fastapi import APIRouter, Depends
from app.services.user_service import get_user_profile
from app.utils.security import get_current_user
from app.utils.responses import success

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def my_profile(current_user: dict = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    profile = get_user_profile(current_user["u_id"])
    return success(profile)


@router.get("/{u_id}")
def user_profile(u_id: int):
    """Return any user's public profile by ID."""
    profile = get_user_profile(u_id)
    return success(profile)
