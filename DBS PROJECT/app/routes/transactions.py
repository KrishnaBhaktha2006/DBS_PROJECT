"""
app/routes/transactions.py
───────────────────────────
GET /transactions/me  → all transactions where the user is buyer OR seller
"""

from fastapi import APIRouter, Depends

from app.services.txn_service import get_user_transactions
from app.utils.security import get_current_user
from app.utils.responses import success

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/me")
def my_transactions(current_user: dict = Depends(get_current_user)):
    """
    Retrieve all transactions for the authenticated user
    (as buyer OR as seller of the listed item).
    Uses a double-JOIN on Users to return both buyer and seller usernames.
    """
    txns = get_user_transactions(u_id=current_user["u_id"])
    return success(txns)
