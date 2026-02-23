"""Callback endpoint for receiving execution results."""

import logging

from fastapi import APIRouter, Depends

from ..connection_manager import ConnectionManager
from ..dependencies import get_connection_manager
from ..schemas import (
    CallbackResponse,
    ExecutionResult,
    WebSocketMessage,
    WebSocketMessageType,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["callbacks"])


@router.post("/callback", response_model=CallbackResponse)
async def receive_callback(
    result: ExecutionResult,
    manager: ConnectionManager = Depends(get_connection_manager),
) -> CallbackResponse:
    """
    Receive execution results from Celery workers.

    Routes to WebSocket subscribers if any are connected.

    Args:
        result: Execution result from Cratos

    Returns:
        Confirmation with delivery status

    Note:
        HTTP callbacks are handled directly by Cratos.
        This gateway only handles WebSocket delivery for real-time notifications.
    """
    task_id = result.task_id
    topic = f"task:{task_id}"

    logger.info(f"Received callback for task {task_id}, status: {result.status}")

    # Check if task has WebSocket subscribers
    has_subscribers = manager.has_subscribers(topic)

    # Route to WebSocket if subscribers exist
    if has_subscribers:
        try:
            message = WebSocketMessage(
                type=WebSocketMessageType.EXECUTION_RESULT,
                task_id=result.task_id,
                status=result.status,
                execution_number=result.execution_number,
                started_at=result.started_at,
                completed_at=result.completed_at,
                duration_seconds=result.duration_seconds,
                http_status_code=result.http_status_code,
                error_type=result.error_type,
                error_message=result.error_message,
                retry_count=result.retry_count,
                is_retry=result.is_retry,
            )

            delivered = await manager.broadcast_to_topic(
                topic, message.model_dump(exclude_none=True)
            )
            logger.info(
                f"Broadcasted to {delivered} WebSocket subscribers for topic {topic}"
            )
        except Exception as e:
            logger.error(f"Failed to broadcast to WebSocket subscribers: {e}")
            # Continue processing even if WebSocket broadcast fails
    else:
        logger.debug(f"No WebSocket subscribers for topic {topic}")

    return CallbackResponse(
        status="received",
        task_id=task_id,
        delivered_via_websocket=has_subscribers,
    )


