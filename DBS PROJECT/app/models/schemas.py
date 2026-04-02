"""
app/models/schemas.py
──────────────────────
Pydantic v2 request / response models.
These are pure validation schemas – NO ORM, no DB mapping.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, EmailStr, field_validator


# ═══════════════════════════════════════════════════
#  AUTH
# ═══════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ═══════════════════════════════════════════════════
#  USERS
# ═══════════════════════════════════════════════════

class UserOut(BaseModel):
    u_id: int
    username: str
    email: str
    phone: Optional[str]
    created_at: datetime


# ═══════════════════════════════════════════════════
#  CATEGORY
# ═══════════════════════════════════════════════════

class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None


class CategoryOut(BaseModel):
    c_id: int
    name: str
    parent_id: Optional[int]
    children: List["CategoryOut"] = []


# ═══════════════════════════════════════════════════
#  LISTING
# ═══════════════════════════════════════════════════

class ListingCreate(BaseModel):
    c_id: int
    title: str
    description: Optional[str] = None
    price: Decimal
    cond: str           # new | like_new | good | fair | poor
    type: str           # buy | sell

    @field_validator("cond")
    @classmethod
    def validate_cond(cls, v):
        allowed = {"new", "like_new", "good", "fair", "poor"}
        if v not in allowed:
            raise ValueError(f"cond must be one of {allowed}")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v not in {"buy", "sell"}:
            raise ValueError("type must be 'buy' or 'sell'")
        return v


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    cond: Optional[str] = None
    status: Optional[str] = None


class ListingOut(BaseModel):
    listing_id: int
    u_id: int
    c_id: int
    title: str
    description: Optional[str]
    price: Decimal
    cond: str
    type: str
    status: str
    created_at: datetime
    # joined fields
    seller_username: Optional[str] = None
    category_name: Optional[str] = None


# ═══════════════════════════════════════════════════
#  OFFER
# ═══════════════════════════════════════════════════

class OfferCreate(BaseModel):
    listing_id: int
    offered_price: Decimal
    message: Optional[str] = None


class OfferOut(BaseModel):
    offer_id: int
    listing_id: int
    buyer_id: int
    offered_price: Decimal
    message: Optional[str]
    status: str
    created_at: datetime
    buyer_username: Optional[str] = None


# ═══════════════════════════════════════════════════
#  TRANSACTION
# ═══════════════════════════════════════════════════

class TxnOut(BaseModel):
    txn_id: int
    offer_id: int
    listing_id: int
    buyer_id: int
    amount: Decimal
    status: str
    txn_date: datetime
    listing_title: Optional[str] = None
    buyer_username: Optional[str] = None


# ═══════════════════════════════════════════════════
#  ALERT
# ═══════════════════════════════════════════════════

class AlertCreate(BaseModel):
    c_id: Optional[int] = None
    price_limit: Optional[Decimal] = None
    keyword: Optional[str] = None


class AlertOut(BaseModel):
    alert_id: int
    u_id: int
    c_id: Optional[int]
    price_limit: Optional[Decimal]
    keyword: Optional[str]
    created_at: datetime


# ═══════════════════════════════════════════════════
#  NOTIFICATION
# ═══════════════════════════════════════════════════

class NotificationOut(BaseModel):
    notif_id: int
    u_id: int
    alert_id: int
    listing_id: int
    seen: bool
    created_at: datetime
    listing_title: Optional[str] = None


# Rebuild CategoryOut so children reference resolves
CategoryOut.model_rebuild()
