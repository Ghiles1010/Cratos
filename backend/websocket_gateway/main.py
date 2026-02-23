"""FastAPI application for WebSocket gateway."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .connection_manager import ConnectionManager
from .routers import callbacks, health, websocket

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("WebSocket Gateway starting up")
    # Initialize connection manager in app state
    app.state.connection_manager = ConnectionManager()
    yield
    # Shutdown
    logger.info("WebSocket Gateway shutting down")


def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Cratos WebSocket Gateway",
        description="Real-time WebSocket notifications for task execution results",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )

    # Include routers
    app.include_router(health.router)
    app.include_router(callbacks.router)
    app.include_router(websocket.router)

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
