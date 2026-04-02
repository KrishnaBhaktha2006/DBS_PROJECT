"""
app/routes/auth.py
───────────────────
POST /auth/register
POST /auth/login
"""

from fastapi import APIRouter
from app.models.schemas import RegisterRequest, LoginRequest
from app.services.auth_service import register_user, login_user
from app.utils.responses import success

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=201)
def register(body: RegisterRequest):
    """Register a new user account."""
    user = register_user(
        username=body.username,
        email=body.email,
        password=body.password,
        phone=body.phone,
    )
    return success(user, "User registered successfully", 201)


@router.post("/login")
def login(body: LoginRequest):
    """Authenticate and receive a JWT bearer token."""
    token_data = login_user(email=body.email, password=body.password)
    return success(token_data, "Login successful")
