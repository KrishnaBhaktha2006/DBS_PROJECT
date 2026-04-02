"""
app/db/connection.py
────────────────────
Database connection pool abstraction layer.

Supports:
  • MySQL  – via mysql-connector-python (pooling built-in)
  • Oracle – via cx_Oracle             (pooling built-in)

The rest of the codebase calls ONLY:
    get_connection()   → context-managed connection
    cursor_execute()   → parameterised query helper
"""

import contextlib
from typing import Any, Generator

from app.config import get_settings

settings = get_settings()

# ──────────────────────────────────────────────────────────────────────────────
#  MySQL pool
# ──────────────────────────────────────────────────────────────────────────────
if settings.DB_DRIVER == "mysql":
    import mysql.connector
    from mysql.connector import pooling

    _mysql_pool = pooling.MySQLConnectionPool(
        pool_name="marketplace_pool",
        pool_size=settings.MYSQL_POOL_SIZE,
        pool_reset_session=True,
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DATABASE,
        autocommit=False,           # we manage transactions explicitly
        charset="utf8mb4",
    )

# ──────────────────────────────────────────────────────────────────────────────
#  Oracle pool
# ──────────────────────────────────────────────────────────────────────────────
elif settings.DB_DRIVER == "oracle":
    import cx_Oracle  # type: ignore

    cx_Oracle.init_oracle_client()          # adjust libdir if needed
    _oracle_pool = cx_Oracle.SessionPool(
        user=settings.ORACLE_USER,
        password=settings.ORACLE_PASSWORD,
        dsn=settings.ORACLE_DSN,
        min=settings.ORACLE_POOL_MIN,
        max=settings.ORACLE_POOL_MAX,
        increment=1,
        threaded=True,
        getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT,
    )
else:
    raise ValueError(f"Unsupported DB_DRIVER: {settings.DB_DRIVER}")


# ──────────────────────────────────────────────────────────────────────────────
#  Public helpers
# ──────────────────────────────────────────────────────────────────────────────

@contextlib.contextmanager
def get_connection():
    """
    Yield a raw DB connection from the pool.
    The caller is responsible for commit / rollback.
    Connection is always returned to the pool on exit.
    """
    if settings.DB_DRIVER == "mysql":
        conn = _mysql_pool.get_connection()
    else:
        conn = _oracle_pool.acquire()
    try:
        yield conn
    finally:
        if settings.DB_DRIVER == "mysql":
            conn.close()          # returns to pool
        else:
            _oracle_pool.release(conn)


def cursor_execute(cursor, sql: str, params: tuple | dict | None = None) -> None:
    """
    Thin wrapper around cursor.execute that normalises parameter style.

    MySQL  uses %s placeholders.
    Oracle uses :name or :1 placeholders.

    For portability, services should pass *tuple* params and use %s
    in SQL strings; this wrapper converts them automatically for Oracle
    by replacing %s → :1, :2 … when the Oracle driver is active.
    """
    if params is None:
        cursor.execute(sql)
        return

    if settings.DB_DRIVER == "oracle" and isinstance(params, tuple):
        # Convert positional %s → :1, :2 … for Oracle
        converted_sql = sql
        for i in range(len(params), 0, -1):
            converted_sql = converted_sql.replace("%s", f":{i}", 1)
        cursor.execute(converted_sql, params)
    else:
        cursor.execute(sql, params)


def last_insert_id(cursor) -> int:
    """
    Return the last auto-generated primary key in a DB-agnostic way.
    """
    if settings.DB_DRIVER == "mysql":
        return cursor.lastrowid
    else:
        # Oracle: caller should use RETURNING id INTO :out and pass outvar
        raise NotImplementedError(
            "For Oracle use 'RETURNING col INTO :out' and handle outvar yourself."
        )
