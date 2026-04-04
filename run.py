#!/usr/bin/env python3
"""
Project launcher.

Initializes the database from schema.sql and insertion.sql, then starts
the FastAPI application with uvicorn.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)


def read_sql_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_sql_statements(sql_text: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []

    for raw_line in sql_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("--"):
            continue
        current.append(raw_line)
        if line.endswith(";"):
            statement = "\n".join(current).strip().rstrip(";").strip()
            if statement:
                statements.append(statement)
            current = []

    trailing = "\n".join(current).strip().rstrip(";").strip()
    if trailing:
        statements.append(trailing)

    return statements


def execute_sql_file(cursor, path: Path) -> None:
    for statement in split_sql_statements(read_sql_file(path)):
        try:
            cursor.execute(statement)
        except Exception as exc:
            print(f"[db] Skipped statement: {exc}")


def apply_migrations(cursor) -> None:
    migration_statements = [
        "ALTER TABLE Notification MODIFY alert_id INT NULL",
        "ALTER TABLE Notification ADD COLUMN event_type VARCHAR(30) NOT NULL DEFAULT 'alert'",
        "ALTER TABLE Notification ADD COLUMN message VARCHAR(255) DEFAULT NULL",
        "CREATE INDEX idx_notification_user_seen ON Notification(u_id, seen)",
    ]
    for statement in migration_statements:
        try:
            cursor.execute(statement)
        except Exception as exc:
            print(f"[db] Skipped migration: {exc}")


def init_database() -> bool:
    import mysql.connector
    from app.config import get_settings

    settings = get_settings()
    schema_path = PROJECT_ROOT / "schema.sql"
    seed_path = PROJECT_ROOT / "insertion.sql"

    print("[db] Initializing database")
    print(f"[db] Host: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}")
    print(f"[db] User: {settings.MYSQL_USER}")
    print(f"[db] Database: {settings.MYSQL_DATABASE}")

    if not schema_path.exists():
        print(f"[db] Missing schema file: {schema_path}")
        return False

    try:
        connection = mysql.connector.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            autocommit=True,
        )
        cursor = connection.cursor()

        execute_sql_file(cursor, schema_path)
        apply_migrations(cursor)
        print("[db] Schema applied")

        if seed_path.exists():
            cursor.execute(f"USE {settings.MYSQL_DATABASE}")
            execute_sql_file(cursor, seed_path)
            print("[db] Sample data applied")

        cursor.close()
        connection.close()
        print("[db] Initialization complete")
        return True
    except Exception as exc:
        print(f"[db] Initialization failed: {exc}")
        print("[db] Check MySQL, credentials, and permissions in .env")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Marketplace application launcher")
    parser.add_argument("--skip-init", action="store_true", help="Skip database initialization")
    parser.add_argument("--no-reload", action="store_true", help="Disable uvicorn auto-reload")
    args = parser.parse_args()

    print("=" * 60)
    print("MARKETPLACE APPLICATION")
    print("=" * 60)

    if not args.skip_init and not init_database():
        print("[db] Continuing without database initialization")

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]
    if not args.no_reload:
        command.append("--reload")

    print("[app] API docs: http://localhost:8000/docs")
    print("[app] Web UI:   http://localhost:8000")

    try:
        subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    except KeyboardInterrupt:
        print("\n[app] Server stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
