"""Routers package."""
from backend.routers.jobs import router as jobs_router
from backend.routers.settings import router as settings_router

__all__ = ["jobs_router", "settings_router"]
