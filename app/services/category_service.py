"""
app/services/category_service.py
Raw-SQL service for category management.

Key query: recursive CTE to fetch the full category tree.
MySQL 8+ supports WITH RECURSIVE; Oracle supports it natively too.
"""

from fastapi import HTTPException, status

from app.db.connection import get_connection, cursor_execute, last_insert_id
from app.config import get_settings

settings = get_settings()


def create_category(name: str, parent_id: int | None) -> dict:
    """
    INSERT a new category.

    SQL:
        -- Validate parent exists (if given)
        SELECT c_id FROM Category WHERE c_id = %s

        -- Insert
        INSERT INTO Category (name, parent_id) VALUES (%s, %s)
    """
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        if parent_id is not None:
            cursor_execute(
                cursor,
                "SELECT c_id FROM Category WHERE c_id = %s",
                (parent_id,),
            )
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent category {parent_id} not found",
                )

        cursor_execute(
            cursor,
            """
            SELECT c_id
            FROM Category
            WHERE LOWER(name) = LOWER(%s)
              AND ((parent_id IS NULL AND %s IS NULL) OR parent_id = %s)
            LIMIT 1
            """,
            (name, parent_id, parent_id),
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category already exists under the selected parent",
            )

        cursor_execute(
            cursor,
            "INSERT INTO Category (name, parent_id) VALUES (%s, %s)",
            (name, parent_id),
        )
        new_id = last_insert_id(cursor)
        conn.commit()
        cursor.close()
        return {"c_id": new_id, "name": name, "parent_id": parent_id, "children": []}


def get_category_tree() -> list[dict]:
    """
    Fetch all categories and build a nested tree in Python.

    SQL (WITH RECURSIVE - works on MySQL 8+ and Oracle 11g+):
    WITH RECURSIVE cat_tree AS (
        SELECT c_id, name, parent_id, 0 AS depth
        FROM Category
        WHERE parent_id IS NULL

        UNION ALL

        SELECT c.c_id, c.name, c.parent_id, ct.depth + 1
        FROM Category c
        JOIN cat_tree ct ON c.parent_id = ct.c_id
    )
    SELECT c_id, name, parent_id, depth
    FROM cat_tree
    ORDER BY depth, parent_id, c_id;
    """
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)

        cursor_execute(
            cursor,
            """
            WITH RECURSIVE cat_tree AS (
                SELECT c_id,
                       name,
                       parent_id,
                       0 AS depth
                FROM Category
                WHERE parent_id IS NULL

                UNION ALL

                SELECT c.c_id,
                       c.name,
                       c.parent_id,
                       ct.depth + 1
                FROM Category c
                JOIN cat_tree ct ON c.parent_id = ct.c_id
            )
            SELECT c_id, name, parent_id, depth
            FROM cat_tree
            ORDER BY depth, parent_id, c_id
            """,
        )
        rows = cursor.fetchall()
        cursor.close()

    node_map: dict[int, dict] = {}
    roots: list[dict] = []

    for row in rows:
        node = {
            "c_id": row["c_id"],
            "name": row["name"],
            "parent_id": row["parent_id"],
            "children": [],
        }
        node_map[row["c_id"]] = node

        if row["parent_id"] is None:
            roots.append(node)
        else:
            parent = node_map.get(row["parent_id"])
            if parent:
                parent["children"].append(node)

    return roots
