"""
app/services/offer_service.py
Raw-SQL service for Offer management.
"""

from decimal import Decimal

from fastapi import HTTPException, status

from app.db.connection import get_connection, cursor_execute, last_insert_id


def create_offer(listing_id: int, buyer_id: int, offered_price: Decimal, message: str | None) -> dict:
    """
    A buyer places an offer on a listing.
    """
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        cursor_execute(
            cursor,
            """
            SELECT l.u_id, l.status, l.title
            FROM Listing l
            WHERE l.listing_id = %s
            """,
            (listing_id,),
        )
        listing = cursor.fetchone()
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
        if listing["status"] != "active":
            raise HTTPException(status_code=400, detail="Listing is not active")
        if listing["u_id"] == buyer_id:
            raise HTTPException(status_code=400, detail="You cannot offer on your own listing")

        cursor_execute(
            cursor,
            """
            INSERT INTO Offer (listing_id, buyer_id, offered_price, message, status)
            VALUES (%s, %s, %s, %s, 'pending')
            """,
            (listing_id, buyer_id, float(offered_price), message),
        )
        offer_id = last_insert_id(cursor)
        cursor_execute(cursor, "SELECT username FROM Users WHERE u_id = %s", (buyer_id,))
        buyer = cursor.fetchone()
        buyer_name = buyer["username"] if buyer else f"User {buyer_id}"
        cursor_execute(
            cursor,
            """
            INSERT INTO Notification (u_id, alert_id, listing_id, event_type, message, seen)
            VALUES (%s, NULL, %s, 'offer_received', %s, 0)
            """,
            (
                listing["u_id"],
                listing_id,
                f"{buyer_name} sent an offer of {float(offered_price):.2f} for '{listing['title']}'.",
            ),
        )
        conn.commit()
        cursor.close()

    return get_offer_by_id(offer_id)


def get_offers_for_listing(listing_id: int, seller_id: int) -> list[dict]:
    """
    Seller views all offers on their listing.
    """
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor_execute(
            cursor,
            """
            SELECT  o.offer_id,
                    o.listing_id,
                    o.buyer_id,
                    o.offered_price,
                    o.message,
                    o.status,
                    o.created_at,
                    u.username AS buyer_username
            FROM    Offer   o
            JOIN    Users   u ON u.u_id       = o.buyer_id
            JOIN    Listing l ON l.listing_id = o.listing_id
            WHERE   o.listing_id = %s
              AND   l.u_id       = %s
            ORDER   BY o.created_at DESC
            """,
            (listing_id, seller_id),
        )
        rows = cursor.fetchall()
        cursor.close()
    return rows


def accept_offer(offer_id: int, seller_id: int) -> dict:
    """
    Accept an offer.
    The database trigger creates the Txn row and marks the listing as sold.
    """
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor_execute(
                cursor,
                """
                SELECT  o.offer_id,
                        o.listing_id,
                        o.buyer_id,
                        o.offered_price,
                        o.status          AS offer_status,
                        l.u_id            AS seller_id,
                        l.status          AS listing_status
                FROM    Offer   o
                JOIN    Listing l ON l.listing_id = o.listing_id
                WHERE   o.offer_id = %s
                """,
                (offer_id,),
            )
            offer = cursor.fetchone()

            if not offer:
                raise HTTPException(status_code=404, detail="Offer not found")
            if offer["seller_id"] != seller_id:
                raise HTTPException(status_code=403, detail="Not your listing")
            if offer["offer_status"] != "pending":
                raise HTTPException(status_code=400, detail="Offer is not pending")
            if offer["listing_status"] != "active":
                raise HTTPException(status_code=400, detail="Listing is not active")

            cursor_execute(
                cursor,
                "UPDATE Offer SET status = 'accepted' WHERE offer_id = %s",
                (offer_id,),
            )

            cursor_execute(
                cursor,
                """
                UPDATE Offer
                SET    status = 'rejected'
                WHERE  listing_id = %s
                  AND  offer_id  != %s
                  AND  status     = 'pending'
                """,
                (offer["listing_id"], offer_id),
            )

            cursor_execute(
                cursor,
                """
                SELECT txn_id
                FROM Txn
                WHERE offer_id = %s
                """,
                (offer_id,),
            )
            txn_row = cursor.fetchone()
            if not txn_row:
                raise HTTPException(
                    status_code=500,
                    detail="Offer was accepted but the database trigger did not create the transaction",
                )
            txn_id = txn_row["txn_id"]

            cursor_execute(
                cursor,
                """
                INSERT INTO Notification (u_id, alert_id, listing_id, event_type, message, seen)
                VALUES (%s, NULL, %s, 'offer_accepted', %s, 0)
                """,
                (
                    offer["buyer_id"],
                    offer["listing_id"],
                    f"Your offer #{offer_id} was accepted.",
                ),
            )

            conn.commit()

        except HTTPException:
            conn.rollback()
            raise
        except Exception as exc:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Transaction failed: {str(exc)}")
        finally:
            cursor.close()

    return {"message": "Offer accepted", "txn_id": txn_id, "offer_id": offer_id}


def reject_offer(offer_id: int, seller_id: int) -> dict:
    """
    Seller rejects a pending offer and the buyer gets a notification.
    """
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor_execute(
            cursor,
            """
            SELECT o.buyer_id, o.listing_id
            FROM Offer o
            JOIN Listing l ON l.listing_id = o.listing_id
            WHERE o.offer_id = %s
              AND o.status = 'pending'
              AND l.u_id = %s
            """,
            (offer_id, seller_id),
        )
        offer = cursor.fetchone()
        if not offer:
            conn.rollback()
            raise HTTPException(
                status_code=403,
                detail="Offer not found, not pending, or not your listing",
            )

        cursor_execute(
            cursor,
            "UPDATE Offer SET status = 'rejected' WHERE offer_id = %s",
            (offer_id,),
        )
        cursor_execute(
            cursor,
            """
            INSERT INTO Notification (u_id, alert_id, listing_id, event_type, message, seen)
            VALUES (%s, NULL, %s, 'offer_rejected', %s, 0)
            """,
            (
                offer["buyer_id"],
                offer["listing_id"],
                f"Your offer #{offer_id} was rejected.",
            ),
        )
        conn.commit()
        cursor.close()

    return {"message": "Offer rejected", "offer_id": offer_id}


def get_offer_by_id(offer_id: int) -> dict:
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor_execute(
            cursor,
            """
            SELECT  o.offer_id,
                    o.listing_id,
                    o.buyer_id,
                    o.offered_price,
                    o.message,
                    o.status,
                    o.created_at,
                    u.username AS buyer_username
            FROM    Offer  o
            JOIN    Users  u ON u.u_id = o.buyer_id
            WHERE   o.offer_id = %s
            """,
            (offer_id,),
        )
        row = cursor.fetchone()
        cursor.close()
    if not row:
        raise HTTPException(status_code=404, detail="Offer not found")
    return row
