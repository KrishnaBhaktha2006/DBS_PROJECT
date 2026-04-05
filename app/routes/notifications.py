"""
app/routes/notifications.py
────────────────────────────
GET   /notifications/me              → all user notifications
PATCH /notifications/{id}/seen       → mark one as seen
"""

from fastapi import APIRouter, Depends

from app.services.notification_service import get_user_notifications, mark_notification_seen, delete_notification
from app.utils.security import get_current_user
from app.utils.responses import success

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/me")
def my_notifications(current_user: dict = Depends(get_current_user)):
    """
    Retrieve all notifications for the authenticated user,
    joined with the triggering listing title.
    """
    notifs = get_user_notifications(u_id=current_user["u_id"])
    return success(notifs)


@router.patch("/{notif_id}/seen")
def mark_seen(notif_id: int, current_user: dict = Depends(get_current_user)):
    """Mark a notification as seen (owner only)."""
    result = mark_notification_seen(notif_id=notif_id, u_id=current_user["u_id"])
    return success(result, "Notification marked as seen")


@router.delete("/{notif_id}")
def delete_one(notif_id: int, current_user: dict = Depends(get_current_user)):
    """Delete a notification (owner only)."""
    result = delete_notification(notif_id=notif_id, u_id=current_user["u_id"])
    return success(result, "Notification deleted")
