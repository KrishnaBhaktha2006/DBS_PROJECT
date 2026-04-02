"""
Database connection helpers with lazy pool initialization.
"""

import contextlib

from fastapi import HTTPException, status

from app.config import get_settings

settings = get_settings()
_mysql_pool = None
_oracle_pool = None


def _build_mysql_pool():
    from mysql.connector import Error as MySQLError, pooling

    try:
        return pooling.MySQLConnectionPool(
            pool_name="marketplace_pool",
            pool_size=settings.MYSQL_POOL_SIZE,
            pool_reset_session=True,
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DATABASE,
            autocommit=False,
            charset="utf8mb4",
        )
    except MySQLError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {exc}",
        ) from exc


def _build_oracle_pool():
    try:
        import cx_Oracle  # type: ignore
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Oracle driver is not installed",
        ) from exc

    try:
        cx_Oracle.init_oracle_client()
    except cx_Oracle.ProgrammingError:
        pass

    try:
        return cx_Oracle.SessionPool(
            user=settings.ORACLE_USER,
            password=settings.ORACLE_PASSWORD,
            dsn=settings.ORACLE_DSN,
            min=settings.ORACLE_POOL_MIN,
            max=settings.ORACLE_POOL_MAX,
            increment=1,
            threaded=True,
            getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT,
        )
    except cx_Oracle.Error as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {exc}",
        ) from exc


def _get_mysql_pool():
    global _mysql_pool
    if _mysql_pool is None:
        _mysql_pool = _build_mysql_pool()
    return _mysql_pool


def _get_oracle_pool():
    global _oracle_pool
    if _oracle_pool is None:
        _oracle_pool = _build_oracle_pool()
    return _oracle_pool


@contextlib.contextmanager
def get_connection():
    if settings.DB_DRIVER == "mysql":
        conn = _get_mysql_pool().get_connection()
    elif settings.DB_DRIVER == "oracle":
        conn = _get_oracle_pool().acquire()
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unsupported DB_DRIVER: {settings.DB_DRIVER}",
        )

    try:
        yield conn
    finally:
        if settings.DB_DRIVER == "mysql":
            conn.close()
        else:
            _get_oracle_pool().release(conn)


def cursor_execute(cursor, sql: str, params: tuple | dict | None = None) -> None:
    if params is None:
        cursor.execute(sql)
        return

    if settings.DB_DRIVER == "oracle" and isinstance(params, tuple):
        converted_sql = sql
        for i in range(len(params), 0, -1):
            converted_sql = converted_sql.replace("%s", f":{i}", 1)
        cursor.execute(converted_sql, params)
    else:
        cursor.execute(sql, params)


def last_insert_id(cursor) -> int:
    if settings.DB_DRIVER == "mysql":
        return cursor.lastrowid
    raise NotImplementedError(
        "For Oracle use 'RETURNING col INTO :out' and handle outvar yourself."
    )
