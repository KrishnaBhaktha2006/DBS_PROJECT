"""
app/services/listing_service.py
────────────────────────────────
Raw-SQL service for Listing CRUD + alert notification generation.

Business logic implemented here (NO database triggers):
  • On create → scan Alert table → INSERT Notification rows
"""

from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status

from app.db.connection import get_connection, cursor_execute, last_insert_id


# ──────────────────────────────────────────────────────────────────────────────
#  CREATE LISTING  +  generate notifications
# ──────────────────────────────────────────────────────────────────────────────

def create_listing(
    u_id: int,
    c_id: int,
    title: str,
    description: Optional[str],
    price: Decimal,
    cond: str,
    listing_type: str,
) -> dict:
    """
    1. INSERT the listing.
    2. Find matching alerts (same transaction, no trigger needed).
    3. INSERT one Notification per matching alert.

    SQL – Match alerts:
    ───────────────────────────────────────────────────────────────
    SELECT alert_id, u_id
    FROM   Alert
    WHERE  (c_id IS NULL OR c_id = %s)            -- category match
      AND  (price_limit IS NULL OR price_limit >= %s)  -- price filter
      AND  (keyword     IS NULL OR %s LIKE CONCAT('%%', keyword, '%%'))  -- keyword
    ───────────────────────────────────────────────────────────────
    """
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # ── 1. INSERT listing ─────────────────────────
            cursor_execute(
                cursor,
                """
                INSERT INTO Listing (u_id, c_id, title, description, price, cond, type, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'active')
                """,
                (u_id, c_id, title, description, float(price), cond, listing_type),
            )
            listing_id = last_insert_id(cursor)

            # ── 2. Find matching alerts ───────────────────
            #    Rules:
            #      • c_id matches (or alert has no c_id filter)
            #      • price <= price_limit (or alert has no price_limit)
            #      • title contains keyword (or alert has no keyword)
            #    We exclude the listing owner from their own notifications.
            cursor_execute(
                cursor,
                """
                SELECT alert_id, u_id
                FROM   Alert
                WHERE  (c_id        IS NULL OR c_id        = %s)
                  AND  (price_limit IS NULL OR price_limit >= %s)
                  AND  (keyword     IS NULL
                        OR %s LIKE CONCAT('%%', keyword, '%%'))
                  AND  u_id != %s
                """,
                (c_id, float(price), title, u_id),
            )
            matching_alerts = cursor.fetchall()

            # ── 3. Bulk-INSERT notifications ──────────────
            if matching_alerts:
                notif_values = [
                    (alert["u_id"], alert["alert_id"], listing_id)
                    for alert in matching_alerts
                ]
                # executemany for batch insert (still parameterised / safe)
                cursor.executemany(
                    """
                    INSERT INTO Notification (u_id, alert_id, listing_id, seen)
                    VALUES (%s, %s, %s, 0)
                    """,
                    notif_values,
                )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()

    return get_listing_by_id(listing_id)


# ──────────────────────────────────────────────────────────────────────────────
#  GET LISTINGS  (with dynamic filters)
# ──────────────────────────────────────────────────────────────────────────────

def get_listings(
    listing_type: Optional[str] = None,
    c_id: Optional[int] = None,
    price_min: Optional[Decimal] = None,
    price_max: Optional[Decimal] = None,
    status: Optional[str] = "active",
) -> list[dict]:
    """
    Fetch listings with optional filters.

    SQL (dynamic WHERE clauses):
    ─────────────────────────────────────────────────────────────────────
    SELECT  l.listing_id, l.u_id, l.c_id, l.title, l.description,
            l.price, l.cond, l.type, l.status, l.created_at,
            u.username  AS seller_username,
            c.name      AS category_name
    FROM    Listing  l
    JOIN    Users    u ON u.u_id = l.u_id
    JOIN    Category c ON c.c_id = l.c_id
    WHERE   l.status = %s          -- and optional filters appended below
    ORDER   BY l.created_at DESC
    ─────────────────────────────────────────────────────────────────────
    """
    sql = """
        SELECT  l.listing_id,
                l.u_id,
                l.c_id,
                l.title,
                l.description,
                l.price,
                l.cond,
                l.type,
                l.status,
                l.created_at,
                u.username  AS seller_username,
                c.name      AS category_name
        FROM    Listing  l
        JOIN    Users    u ON u.u_id  = l.u_id
        JOIN    Category c ON c.c_id  = l.c_id
        WHERE   1 = 1
    """
    params: list = []

    if status:
        sql += " AND l.status = %s"
        params.append(status)

    if listing_type:
        sql += " AND l.type = %s"
        params.append(listing_type)

    if c_id is not None:
        sql += " AND l.c_id = %s"
        params.append(c_id)

    if price_min is not None:
        sql += " AND l.price >= %s"
        params.append(float(price_min))

    if price_max is not None:
        sql += " AND l.price <= %s"
        params.append(float(price_max))

    sql += " ORDER BY l.created_at DESC"

    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor_execute(cursor, sql, tuple(params))
        rows = cursor.fetchall()
        cursor.close()

    return rows


# ──────────────────────────────────────────────────────────────────────────────
#  GET SINGLE LISTING
# ──────────────────────────────────────────────────────────────────────────────

def get_listing_by_id(listing_id: int) -> dict:
    """
    SQL:
        SELECT l.*, u.username AS seller_username, c.name AS category_name
        FROM   Listing  l
        JOIN   Users    u ON u.u_id = l.u_id
        JOIN   Category c ON c.c_id = l.c_id
        WHERE  l.listing_id = %s
    """
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor_execute(
            cursor,
            """
            SELECT  l.listing_id,
                    l.u_id,
                    l.c_id,
                    l.title,
                    l.description,
                    l.price,
                    l.cond,
                    l.type,
                    l.status,
                    l.created_at,
                    u.username  AS seller_username,
                    c.name      AS category_name
            FROM    Listing  l
            JOIN    Users    u ON u.u_id = l.u_id
            JOIN    Category c ON c.c_id = l.c_id
            WHERE   l.listing_id = %s
            """,
            (listing_id,),
        )
        row = cursor.fetchone()
        cursor.close()

    if not row:
        raise HTTPException(status_code=404, detail="Listing not found")
    return row


# ──────────────────────────────────────────────────────────────────────────────
#  UPDATE LISTING
# ──────────────────────────────────────────────────────────────────────────────

def update_listing(listing_id: int, u_id: int, updates: dict) -> dict:
    """
    Dynamically build SET clause – only update provided fields.

    SQL:
        UPDATE Listing
        SET    title = %s, price = %s, ...   -- only changed fields
        WHERE  listing_id = %s AND u_id = %s -- owner check
    """
    # Remove None values – don't update fields the user didn't send
    fields = {k: v for k, v in updates.items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clauses = ", ".join(f"{col} = %s" for col in fields)
    params = list(fields.values()) + [listing_id, u_id]

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor_execute(
            cursor,
            f"UPDATE Listing SET {set_clauses} WHERE listing_id = %s AND u_id = %s",
            tuple(params),
        )
        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(
                status_code=403,
                detail="Listing not found or you are not the owner",
            )
        conn.commit()
        cursor.close()

    return get_listing_by_id(listing_id)


# ──────────────────────────────────────────────────────────────────────────────
#  DELETE LISTING
# ──────────────────────────────────────────────────────────────────────────────

def delete_listing(listing_id: int, u_id: int) -> dict:
    """
    Soft-delete: set status = 'closed' (owner only).

    SQL:
        UPDATE Listing
        SET    status = 'closed'
        WHERE  listing_id = %s AND u_id = %s
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor_execute(
            cursor,
            "UPDATE Listing SET status = 'closed' WHERE listing_id = %s AND u_id = %s",
            (listing_id, u_id),
        )
        if cursor.rowcount == 0:
            conn.rollback()
            raise HTTPException(
                status_code=403,
                detail="Listing not found or you are not the owner",
            )
        conn.commit()
        cursor.close()

    return {"listing_id": listing_id, "status": "closed"}
