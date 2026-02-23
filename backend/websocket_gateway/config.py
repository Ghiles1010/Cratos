"""Configuration settings for the WebSocket gateway."""

import os
from typing import List


class Settings:
    """Application settings."""

    # CORS settings
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", "*"
    ).split(",") if os.getenv("CORS_ORIGINS") != "*" else ["*"]
    CORS_CREDENTIALS: bool = os.getenv("CORS_CREDENTIALS", "true").lower() == "true"
    CORS_METHODS: List[str] = os.getenv("CORS_METHODS", "*").split(",")
    CORS_HEADERS: List[str] = os.getenv("CORS_HEADERS", "*").split(",")

    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()

