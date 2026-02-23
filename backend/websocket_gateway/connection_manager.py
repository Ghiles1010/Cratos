"""WebSocket connection manager."""

import logging
from typing import Dict, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections by topic."""

    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, topic: str) -> None:
        """Accept and register a WebSocket connection for a topic."""
        await websocket.accept()
        if topic not in self.active_connections:
            self.active_connections[topic] = set()
        self.active_connections[topic].add(websocket)
        logger.info(f"WebSocket connected for topic: {topic}")

    def disconnect(self, websocket: WebSocket, topic: str) -> None:
        """Remove a WebSocket connection from a topic."""
        if topic in self.active_connections:
            self.active_connections[topic].discard(websocket)
            if not self.active_connections[topic]:
                del self.active_connections[topic]
        logger.info(f"WebSocket disconnected for topic: {topic}")

    def has_subscribers(self, topic: str) -> bool:
        """Check if a topic has any active subscribers."""
        return (
            topic in self.active_connections
            and len(self.active_connections[topic]) > 0
        )

    def get_subscriber_count(self, topic: str) -> int:
        """Get the number of subscribers for a topic."""
        if topic not in self.active_connections:
            return 0
        return len(self.active_connections[topic])

    async def broadcast_to_topic(
        self, topic: str, message: dict
    ) -> int:
        """
        Broadcast a message to all subscribers of a topic.

        Returns:
            Number of successful deliveries
        """
        if topic not in self.active_connections:
            return 0

        disconnected = set()
        successful = 0

        for ws in self.active_connections[topic]:
            try:
                await ws.send_json(message)
                successful += 1
            except Exception as e:
                logger.warning(f"Failed to send to WebSocket: {e}")
                disconnected.add(ws)

        # Clean up disconnected clients
        if disconnected:
            self.active_connections[topic] -= disconnected
            if not self.active_connections[topic]:
                del self.active_connections[topic]

        return successful

    def get_total_connections(self) -> int:
        """Get total number of active connections across all topics."""
        return sum(len(connections) for connections in self.active_connections.values())



