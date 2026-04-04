"""
app/routes/listings.py
───────────────────────
POST   /listings                → create listing
GET    /listings                → list with filters
GET    /listings/{listing_id}   → single listing
PUT    /listings/{listing_id}   → update listing
DELETE /listings/{listing_id}   → soft-delete listing
"""

from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.models.schemas import ListingCreate, ListingUpdate
from app.services.listing_service import (
    create_listing, get_listings, get_listing_by_id,
    update_listing, delete_listing,
)
from app.utils.security import get_current_user
from app.utils.responses import success

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.post("/", status_code=201)
def create(body: ListingCreate):
    """
    Create a new listing.
    Automatically generates Notifications for matching Alerts.
    """
    mock_u_id = 1
    listing = create_listing(
        u_id=mock_u_id,
        c_id=body.c_id,
        title=body.title,
        description=body.description,
        price=body.price,
        cond=body.cond,
        listing_type=body.type,
    )
    return success(listing, "Listing created", 201)


@router.get("/")
def list_all(
    type: Optional[str]    = Query(None, description="buy | sell"),
    c_id: Optional[int]    = Query(None, description="Category ID"),
    price_min: Optional[Decimal] = Query(None),
    price_max: Optional[Decimal] = Query(None),
    status: Optional[str]  = Query("active", description="active | sold | closed | fulfilled"),
):
    """
    Retrieve listings with optional filters.
    Supports: type, category, price range, and status.
    """
    listings = get_listings(
        listing_type=type,
        c_id=c_id,
        price_min=price_min,
        price_max=price_max,
        status=status,
    )
    return success(listings)


@router.get("/{listing_id}")
def get_one(listing_id: int):
    """Retrieve a single listing by ID (with seller and category info)."""
    listing = get_listing_by_id(listing_id)
    return success(listing)


@router.put("/{listing_id}")
def update(
    listing_id: int,
    body: ListingUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update listing fields (owner only). Only send fields you want to change."""
    updated = update_listing(
        listing_id=listing_id,
        u_id=current_user["u_id"],
        updates=body.model_dump(exclude_unset=True),
    )
    return success(updated, "Listing updated")


@router.delete("/{listing_id}")
def delete(listing_id: int, current_user: dict = Depends(get_current_user)):
    """Soft-delete a listing by setting its status to 'closed' (owner only)."""
    result = delete_listing(listing_id=listing_id, u_id=current_user["u_id"])
    return success(result, "Listing closed")
