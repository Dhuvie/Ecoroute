"""
EcoRoute Backend - Main FastAPI Application
===========================================

Wires together every router, configures CORS, logging, lifespan events,
and exposes the OpenAPI schema.

Run:
    uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# Make sure the project root is on sys.path so `ml` package is importable
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from .core.config import settings
from .core.database import init_db
from .core.logging_config import configure_logging
from .api.routers import analytics, deliveries, fleet, fuel, routes, vehicles

logger = logging.getLogger("ecoroute.main")


# --------------------------------------------------------------------------- #
# Lifespan
# --------------------------------------------------------------------------- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup + shutdown hooks."""
    configure_logging("INFO")
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    init_db()

    # Seed demo data on first run
    from .utils.seeder import seed_demo_data
    seed_demo_data()

    logger.info("Application ready")
    yield
    logger.info("Application shutting down")


# --------------------------------------------------------------------------- #
# App
# --------------------------------------------------------------------------- #
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "ML-driven logistics route optimization that reduces fuel consumption "
        "by approximately 18% across large delivery networks."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------- #
# Routers
# --------------------------------------------------------------------------- #
api_prefix = settings.api_prefix
app.include_router(vehicles.router, prefix=api_prefix)
app.include_router(deliveries.router, prefix=api_prefix)
app.include_router(fuel.router, prefix=api_prefix)
app.include_router(routes.router, prefix=api_prefix)
app.include_router(fleet.router, prefix=api_prefix)
app.include_router(analytics.router, prefix=api_prefix)


# --------------------------------------------------------------------------- #
# Root + health
# --------------------------------------------------------------------------- #
@app.get("/", include_in_schema=False)
def root():
    """Redirect to interactive API docs."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["health"])
def health():
    """Liveness + readiness probe."""
    from .services.fuel_service import fuel_service
    from .core.database import engine
    from sqlalchemy import text

    db_ready = True
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_ready = False

    return {
        "status": "ok",
        "version": settings.app_version,
        "model_loaded": fuel_service.is_ready,
        "model_name": (
            fuel_service._predictor.model_name if fuel_service.is_ready else None
        ),
        "database_ready": db_ready,
    }


@app.get("/api/v1/_meta", tags=["meta"])
def meta():
    """Project metadata for the frontend."""
    return {
        "name": "EcoRoute",
        "version": settings.app_version,
        "tagline": "ML-driven logistics route optimization that reduces fuel consumption by ~18% across large delivery networks.",
        "endpoints": {
            "vehicles": f"{api_prefix}/vehicles",
            "deliveries": f"{api_prefix}/deliveries",
            "fuel_predict": f"{api_prefix}/fuel/predict",
            "route_optimize": f"{api_prefix}/routes/optimize",
            "fleet_optimize": f"{api_prefix}/fleet/optimize",
            "analytics_summary": f"{api_prefix}/analytics/summary",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
