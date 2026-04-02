"""
app/services/user_service.py
─────────────────────────────
Raw-SQL service for user profile operations.
"""

from fastapi import HTTPException, status

from app.db.connection import get_connection, cursor_execute


def get_user_profile(u_id: int) -> dict:
    """
    Fetch public profile of a single user.

    SQL:
        SELECT u_id, username, email, phone, created_at
        FROM Users
        WHERE u_id = %s
    """
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor_execute(
            cursor,
            """
            SELECT u_id, username, email, phone, created_at
            FROM   Users
            WHERE  u_id = %s
            """,
            (u_id,),
        )
        user = cursor.fetchone()
        cursor.close()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user
