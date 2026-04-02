"""
app/routes/offers.py
─────────────────────
POST   /offers                         → buyer creates an offer
GET    /offers/listing/{listing_id}    → seller views offers on their listing
POST   /offers/{offer_id}/accept       → seller accepts an offer (triggers Txn + sold)
POST   /offers/{offer_id}/reject       → seller rejects an offer
"""

from fastapi import APIRouter, Depends

from app.models.schemas import OfferCreate
from app.services.offer_service import (
    create_offer, get_offers_for_listing, accept_offer, reject_offer,
)
from app.utils.security import get_current_user
from app.utils.responses import success

router = APIRouter(prefix="/offers", tags=["Offers"])


@router.post("/", status_code=201)
def create(body: OfferCreate, current_user: dict = Depends(get_current_user)):
    """Place a new offer on an active listing."""
    offer = create_offer(
        listing_id=body.listing_id,
        buyer_id=current_user["u_id"],
        offered_price=body.offered_price,
        message=body.message,
    )
    return success(offer, "Offer placed", 201)


@router.get("/listing/{listing_id}")
def listing_offers(listing_id: int, current_user: dict = Depends(get_current_user)):
    """
    Seller retrieves all offers on one of their listings.
    Returns 403 if the caller does not own the listing.
    """
    offers = get_offers_for_listing(
        listing_id=listing_id,
        seller_id=current_user["u_id"],
    )
    return success(offers)


@router.post("/{offer_id}/accept")
def accept(offer_id: int, current_user: dict = Depends(get_current_user)):
    """
    Accept a pending offer.
    This triggers an atomic DB transaction:
      • Offer → accepted
      • All other pending offers → rejected
      • Txn record created
      • Listing → sold
    """
    result = accept_offer(offer_id=offer_id, seller_id=current_user["u_id"])
    return success(result, "Offer accepted and transaction created")


@router.post("/{offer_id}/reject")
def reject(offer_id: int, current_user: dict = Depends(get_current_user)):
    """Reject a pending offer (seller only)."""
    result = reject_offer(offer_id=offer_id, seller_id=current_user["u_id"])
    return success(result, "Offer rejected")
