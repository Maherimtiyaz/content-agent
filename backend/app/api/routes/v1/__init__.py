"""API v1 routes."""

from .brand_profiles import router as brand_profiles_router
from .knowledge_items import router as knowledge_items_router

__all__ = [
    "brand_profiles_router",
    "knowledge_items_router",
]
