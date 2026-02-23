"""WebSocket subscription endpoint."""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..connection_manager import ConnectionManager
from ..schemas import WebSocketMessage, WebSocketMessageType

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/subscribe/{topic}")
async def websocket_subscribe(websocket: WebSocket, topic: str):
    """
    WebSocket endpoint for subscribing to task execution results.

    Args:
        websocket: WebSocket connection
        topic: Topic to subscribe to (e.g., "task:uuid" or "user:123")

    Example:
        ```javascript
        const ws = new WebSocket('ws://localhost:8000/ws/subscribe/task:abc-123');
        ws.onmessage = (event) => {
          const result = JSON.parse(event.data);
          console.log('Task completed:', result.status);
        };
        ```
    """
    # Get connection manager from app state
    manager: ConnectionManager = websocket.app.state.connection_manager

    try:
        await manager.connect(websocket, topic)

        # Send confirmation
        confirmation = WebSocketMessage(
            type=WebSocketMessageType.SUBSCRIBED,
            topic=topic,
            message="Successfully subscribed to topic",
        )
        await websocket.send_json(confirmation.model_dump(exclude_none=True))

        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()

            # Handle ping/pong for keepalive
            if data == "ping":
                await websocket.send_text("pong")
            elif data == "unsubscribe":
                break
            else:
                logger.debug(f"Received message from {topic}: {data}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for topic: {topic}")
    finally:
        manager.disconnect(websocket, topic)


