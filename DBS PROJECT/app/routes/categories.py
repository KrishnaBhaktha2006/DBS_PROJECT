"""
app/routes/categories.py
─────────────────────────
POST /categories          → create category (auth required)
GET  /categories/tree     → full recursive tree
"""

from fastapi import APIRouter, Depends
from app.models.schemas import CategoryCreate
from app.services.category_service import create_category, get_category_tree
from app.utils.security import get_current_user
from app.utils.responses import success

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", status_code=201)
def create(body: CategoryCreate, _: dict = Depends(get_current_user)):
    """Create a new category (optionally nested under a parent)."""
    cat = create_category(name=body.name, parent_id=body.parent_id)
    return success(cat, "Category created", 201)


@router.get("/tree")
def category_tree():
    """
    Return the complete hierarchical category tree.
    Uses a WITH RECURSIVE CTE internally.
    """
    tree = get_category_tree()
    return success(tree)
