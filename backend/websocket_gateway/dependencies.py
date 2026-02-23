"""Dependencies for the WebSocket gateway."""

from fastapi import Request

from .connection_manager import ConnectionManager


def get_connection_manager(request: Request) -> ConnectionManager:
    """
    Dependency to get the connection manager from app state.

    Args:
        request: FastAPI request object

    Returns:
        ConnectionManager instance
    """
    return request.app.state.connection_manager

