"""
app/services/alert_service.py
──────────────────────────────
Raw-SQL service for user price/keyword Alerts.
"""

from decimal import Decimal
from typing import Optional

from fastapi import HTTPException

from app.db.connection import get_connection, cursor_execute, last_insert_id


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
        conn.commit()
        cursor.close()

    return {
        "alert_id": alert_id,
        "u_id": u_id,
        "c_id": c_id,
        "price_limit": price_limit,
        "keyword": keyword,
    }


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
