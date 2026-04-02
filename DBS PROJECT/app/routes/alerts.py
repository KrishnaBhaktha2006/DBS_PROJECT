"""
app/routes/alerts.py
─────────────────────
POST   /alerts          → create alert
GET    /alerts/me       → user's alerts
DELETE /alerts/{id}     → delete alert
"""

from fastapi import APIRouter, Depends

from app.models.schemas import AlertCreate
from app.services.alert_service import create_alert, get_user_alerts, delete_alert
from app.utils.security import get_current_user
from app.utils.responses import success

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("/", status_code=201)
def create(body: AlertCreate, current_user: dict = Depends(get_current_user)):
    """
    Create a price/keyword alert.
    At least one of c_id, price_limit, or keyword must be provided.
    """
    alert = create_alert(
        u_id=current_user["u_id"],
        c_id=body.c_id,
        price_limit=body.price_limit,
        keyword=body.keyword,
    )
    return success(alert, "Alert created", 201)


@router.get("/me")
def my_alerts(current_user: dict = Depends(get_current_user)):
    """Retrieve all alerts created by the authenticated user."""
    alerts = get_user_alerts(u_id=current_user["u_id"])
    return success(alerts)


@router.delete("/{alert_id}")
def delete(alert_id: int, current_user: dict = Depends(get_current_user)):
    """Delete an alert owned by the authenticated user."""
    result = delete_alert(alert_id=alert_id, u_id=current_user["u_id"])
    return success(result, "Alert deleted")
