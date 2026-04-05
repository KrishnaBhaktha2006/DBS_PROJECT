"""
app/services/alert_service.py
──────────────────────────────
Raw-SQL service for user price/keyword Alerts.
"""

from decimal import Decimal
from typing import Optional

from fastapi import HTTPException

from app.db.connection import get_connection, cursor_execute, last_insert_id


def _normalize_keyword(keyword: Optional[str]) -> Optional[str]:
    if keyword is None:
        return None
    cleaned = keyword.strip()
    return cleaned or None


def _create_notifications_for_existing_matches(cursor, *, alert_id: int, u_id: int, c_id: Optional[int], price_limit: Optional[Decimal], keyword: Optional[str]) -> None:
    keyword = _normalize_keyword(keyword)
    cursor_execute(
        cursor,
        """
        SELECT l.listing_id, l.title
        FROM Listing l
        JOIN Category c ON c.c_id = l.c_id
        WHERE l.status = 'active'
          AND l.type = 'sell'
          AND l.u_id != %s
          AND (%s IS NULL OR l.c_id = %s)
          AND (%s IS NULL OR l.price <= %s)
          AND (
                %s IS NULL
                OR LOWER(l.title) LIKE CONCAT('%%', LOWER(%s), '%%')
                OR LOWER(COALESCE(l.description, '')) LIKE CONCAT('%%', LOWER(%s), '%%')
                OR LOWER(c.name) LIKE CONCAT('%%', LOWER(%s), '%%')
              )
        ORDER BY l.created_at DESC
        """,
        (
            u_id,
            c_id, c_id,
            float(price_limit) if price_limit is not None else None,
            float(price_limit) if price_limit is not None else None,
            keyword, keyword, keyword, keyword,
        ),
    )
    matching_listings = cursor.fetchall()

    for listing in matching_listings:
        cursor_execute(
            cursor,
            """
            INSERT INTO Notification (u_id, alert_id, listing_id, event_type, message, seen)
            SELECT %s, %s, %s, 'alert', %s, 0
            WHERE NOT EXISTS (
                SELECT 1
                FROM Notification
                WHERE u_id = %s
                  AND alert_id = %s
                  AND listing_id = %s
                  AND event_type = 'alert'
            )
            """,
            (
                u_id,
                alert_id,
                listing["listing_id"],
                f"Existing listing '{listing['title']}' already matches your alert.",
                u_id,
                alert_id,
                listing["listing_id"],
            ),
        )


def create_alert(
    u_id: int,
    c_id: Optional[int],
    price_limit: Optional[Decimal],
    keyword: Optional[str],
) -> dict:
    """
    INSERT a new alert for the authenticated user.

    SQL:
        INSERT INTO Alert (u_id, c_id, price_limit, keyword)
        VALUES (%s, %s, %s, %s)
    """
    if not any([c_id, price_limit is not None, keyword]):
        raise HTTPException(
            status_code=400,
            detail="At least one of c_id, price_limit, or keyword must be set",
        )

    keyword = _normalize_keyword(keyword)

    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor_execute(
            cursor,
            """
            INSERT INTO Alert (u_id, c_id, price_limit, keyword)
            VALUES (%s, %s, %s, %s)
            """,
            (u_id, c_id, float(price_limit) if price_limit is not None else None, keyword),
        )
        alert_id = last_insert_id(cursor)
        _create_notifications_for_existing_matches(
            cursor,
            alert_id=alert_id,
            u_id=u_id,
            c_id=c_id,
            price_limit=price_limit,
            keyword=keyword,
        )
        conn.commit()
        cursor.close()

    return {
        "alert_id": alert_id,
        "u_id": u_id,
        "c_id": c_id,
        "price_limit": price_limit,
        "keyword": keyword,
    }


def sync_user_alert_notifications(u_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor_execute(
            cursor,
            """
            SELECT alert_id, c_id, price_limit, keyword
            FROM Alert
            WHERE u_id = %s
            """,
            (u_id,),
        )
        alerts = cursor.fetchall()

        for alert in alerts:
            _create_notifications_for_existing_matches(
                cursor,
                alert_id=alert["alert_id"],
                u_id=u_id,
                c_id=alert["c_id"],
                price_limit=alert["price_limit"],
                keyword=alert["keyword"],
            )

        conn.commit()
        cursor.close()


def get_user_alerts(u_id: int) -> list[dict]:
    """
    Fetch all alerts owned by the user.

    SQL:
        SELECT alert_id, u_id, c_id, price_limit, keyword, created_at
        FROM   Alert
        WHERE  u_id = %s
        ORDER  BY created_at DESC
    """
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor_execute(
            cursor,
            """
            SELECT alert_id, u_id, c_id, price_limit, keyword, created_at
            FROM   Alert
            WHERE  u_id = %s
            ORDER  BY created_at DESC
            """,
            (u_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
    return rows


def delete_alert(alert_id: int, u_id: int) -> dict:
    """
    Delete an alert (owner only).

    SQL:
        DELETE FROM Alert WHERE alert_id = %s AND u_id = %s
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        # Detach notifications first to satisfy FK constraints when removing an alert.
        cursor_execute(
            cursor,
            """
            UPDATE Notification n
            JOIN Alert a ON a.alert_id = n.alert_id
            SET n.alert_id = NULL
            WHERE n.alert_id = %s
              AND a.u_id = %s
            """,
            (alert_id, u_id),
        )
        cursor_execute(
            cursor,
            "DELETE FROM Alert WHERE alert_id = %s AND u_id = %s",
            (alert_id, u_id),
        )
        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(status_code=403, detail="Alert not found or not yours")
        conn.commit()
        cursor.close()
    return {"message": "Alert deleted", "alert_id": alert_id}
