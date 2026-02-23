"""Health check endpoint."""

from fastapi import APIRouter, Depends

from ..connection_manager import ConnectionManager
from ..dependencies import get_connection_manager
from ..schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(
    manager: ConnectionManager = Depends(get_connection_manager),
):
    """
    Health check endpoint.

    Returns:
        Health status and number of active WebSocket connections
    """
    return HealthResponse(
        status="healthy",
        connections=manager.get_total_connections(),
    )


