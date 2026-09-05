"""Health check endpoint."""

from fastapi import APIRouter
from app.schemas.common import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
@router.get("/", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Check if the API is running.
    
    Returns:
        Health status with optional version information.
    """
    return HealthResponse(status="healthy", version="0.1.0")
