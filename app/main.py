"""
app/main.py
────────────
FastAPI application entry point.

• Registers all route groups
• Adds global exception handlers for clean JSON errors
• Exposes OpenAPI docs at /docs and /redoc
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import (
    auth_router,
    users_router,
    categories_router,
    listings_router,
    offers_router,
    transactions_router,
    alerts_router,
    notifications_router,
)

settings = get_settings()

# ──────────────────────────────────────────────────────────────────────────────
#  Application factory
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Online Marketplace API",
    description=(
        "A marketplace backend built with FastAPI and raw SQL queries. "
        "Supports listings, offers, transactions, alerts, and notifications."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (open for development – restrict in production) ──────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────────────────────────────────────
#  Global exception handlers
# ──────────────────────────────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler so unhandled errors return JSON, not HTML."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "Internal server error", "detail": str(exc)},
    )


# ──────────────────────────────────────────────────────────────────────────────
#  Route registration
# ──────────────────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(listings_router)
app.include_router(offers_router)
app.include_router(transactions_router)
app.include_router(alerts_router)
app.include_router(notifications_router)


# ──────────────────────────────────────────────────────────────────────────────
#  Health check
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "environment": settings.APP_ENV}


# ──────────────────────────────────────────────────────────────────────────────
#  Static files and SPA routing
# ──────────────────────────────────────────────────────────────────────────────

from fastapi.responses import FileResponse
from pathlib import Path

frontend_dir = Path(__file__).parent.parent / "frontend"

@app.get("/", include_in_schema=False)
async def root():
    """Serve index.html for root path"""
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(
            str(index_path),
            media_type="text/html",
            headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
        )
    return {"detail": "index.html not found"}, 404

@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    """Serve static files or index.html for SPA routing"""
    file_path = frontend_dir / full_path
    no_cache_headers = {"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"}
    
    # If it's an existing file, serve it
    if file_path.is_file() and file_path.exists():
        return FileResponse(str(file_path), headers=no_cache_headers)
    
    # Otherwise serve index.html (SPA routing)
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(
            str(index_path),
            media_type="text/html",
            headers=no_cache_headers,
        )
    
    return {"detail": "Not Found"}, 404


# ──────────────────────────────────────────────────────────────────────────────
#  Dev runner  (python app/main.py)
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=(settings.APP_ENV == "development"),
    )
