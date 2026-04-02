"""
app/services/auth_service.py
─────────────────────────────
Raw-SQL service for user registration and login.
"""

from fastapi import HTTPException, status

from app.db.connection import get_connection, cursor_execute, last_insert_id
from app.utils.security import hash_password, verify_password, create_access_token


def register_user(username: str, email: str, password: str, phone: str | None) -> dict:
    """
    INSERT a new user after checking for duplicate username / email.

    SQL:
        -- Check duplicates
        SELECT u_id FROM Users WHERE username = %s OR email = %s

        -- Insert
        INSERT INTO Users (username, email, password_hash, phone)
        VALUES (%s, %s, %s, %s)
    """
    hashed = hash_password(password)

    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        # ── Guard: duplicate check ────────────────────────
        cursor_execute(
            cursor,
            "SELECT u_id FROM Users WHERE username = %s OR email = %s",
            (username, email),
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or email already exists",
            )

        # ── Insert new user ───────────────────────────────
        cursor_execute(
            cursor,
            """
            INSERT INTO Users (username, email, password_hash, phone)
            VALUES (%s, %s, %s, %s)
            """,
            (username, email, hashed, phone),
        )
        new_id = last_insert_id(cursor)
        conn.commit()

        cursor.close()
        return {"u_id": new_id, "username": username, "email": email}


def login_user(email: str, password: str) -> dict:
    """
    Verify credentials and return a JWT access token.

    SQL:
        SELECT u_id, username, email, password_hash
        FROM Users
        WHERE email = %s
    """
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        cursor_execute(
            cursor,
            "SELECT u_id, username, email, password_hash FROM Users WHERE email = %s",
            (email,),
        )
        user = cursor.fetchone()
        cursor.close()

    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(
        {"sub": str(user["u_id"]), "username": user["username"], "email": user["email"]}
    )
    return {"access_token": token, "token_type": "bearer"}
