"""
app/services/txn_service.py
────────────────────────────
Raw-SQL service for viewing Transactions.
Transactions are created only by offer_service.accept_offer().
"""

from app.db.connection import get_connection, cursor_execute


def get_user_transactions(u_id: int) -> list[dict]:
    """
    Fetch all transactions where the user is the buyer OR the seller.

    SQL:
    ─────────────────────────────────────────────────────────────────────
    SELECT  t.txn_id,
            t.offer_id,
            t.listing_id,
            t.buyer_id,
            t.amount,
            t.status,
            t.txn_date,
            l.title        AS listing_title,
            buyer.username AS buyer_username,
            seller.username AS seller_username
    FROM    Txn     t
    JOIN    Listing l      ON l.listing_id = t.listing_id
    JOIN    Users   buyer  ON buyer.u_id   = t.buyer_id
    JOIN    Users   seller ON seller.u_id  = l.u_id
    WHERE   t.buyer_id = %s          -- user is buyer
       OR   l.u_id     = %s          -- user is seller
    ORDER   BY t.txn_date DESC
    ─────────────────────────────────────────────────────────────────────
    Note the SELF-JOIN on Users to get both buyer and seller usernames.
    """
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor_execute(
            cursor,
            """
            SELECT  t.txn_id,
                    t.offer_id,
                    t.listing_id,
                    t.buyer_id,
                    t.amount,
                    t.status,
                    t.txn_date,
                    l.title          AS listing_title,
                    buyer.username   AS buyer_username,
                    seller.username  AS seller_username
            FROM    Txn     t
            JOIN    Listing l       ON l.listing_id = t.listing_id
            JOIN    Users   buyer   ON buyer.u_id   = t.buyer_id
            JOIN    Users   seller  ON seller.u_id  = l.u_id
            WHERE   t.buyer_id = %s
               OR   l.u_id     = %s
            ORDER   BY t.txn_date DESC
            """,
            (u_id, u_id),
        )
        rows = cursor.fetchall()
        cursor.close()

    return rows
