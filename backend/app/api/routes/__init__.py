"""API routes."""

from .health import router as health_router
from .v1.brand_profiles import router as brand_profiles_router
from .v1.knowledge_items import router as knowledge_items_router

__all__ = [
    "health_router",
    "brand_profiles_router",
    "knowledge_items_router",
]
