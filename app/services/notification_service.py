"""
app/services/notification_service.py
──────────────────────────────────────
Raw-SQL service for user Notifications.
Notifications are INSERT-ed by listing_service.create_listing().
This service only handles READ and MARK-AS-SEEN.
"""

from fastapi import HTTPException

from app.db.connection import get_connection, cursor_execute


def get_user_notifications(u_id: int) -> list[dict]:
    """
    Fetch all notifications for the authenticated user,
    newest first, with the matching listing title attached.

    SQL:
    ─────────────────────────────────────────────────────────────────────
    SELECT  n.notif_id,
            n.u_id,
            n.alert_id,
            n.listing_id,
            n.seen,
            n.created_at,
            l.title AS listing_title
    FROM    Notification  n
    JOIN    Listing       l ON l.listing_id = n.listing_id
    WHERE   n.u_id = %s
    ORDER   BY n.created_at DESC
    ─────────────────────────────────────────────────────────────────────
    """
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor_execute(
            cursor,
            """
            SELECT  n.notif_id,
                    n.u_id,
                    n.alert_id,
                    n.listing_id,
                    n.event_type,
                    n.message,
                    n.seen,
                    n.created_at,
                    l.title AS listing_title
            FROM    Notification  n
            JOIN    Listing       l ON l.listing_id = n.listing_id
            WHERE   n.u_id = %s
            ORDER   BY n.created_at DESC
            """,
            (u_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
    return rows


def mark_notification_seen(notif_id: int, u_id: int) -> dict:
    """
    Mark a single notification as seen (owner only).

    SQL:
        UPDATE Notification
        SET    seen = 1
        WHERE  notif_id = %s AND u_id = %s
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor_execute(
            cursor,
            "UPDATE Notification SET seen = 1 WHERE notif_id = %s AND u_id = %s",
            (notif_id, u_id),
        )
        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(
                status_code=403,
                detail="Notification not found or not yours",
            )
        conn.commit()
        cursor.close()
    return {"message": "Marked as seen", "notif_id": notif_id}
