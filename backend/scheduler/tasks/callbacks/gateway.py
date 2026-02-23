import logging
import os

import requests

from ..models import TaskExecution, TaskSchedule

logger = logging.getLogger(__name__)

GATEWAY_URL = os.getenv("WEBSOCKET_GATEWAY_URL", None)


def notify(task: TaskSchedule, execution: TaskExecution, response, exception) -> None:
    """Send execution result to WebSocket gateway. No-op if gateway is not configured."""
    if not GATEWAY_URL:
        return

    try:
        payload = {
            "task_id": str(task.task_id),
            "status": execution.status,
            "execution_number": execution.execution_number,
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "duration_seconds": execution.duration_seconds,
            "retry_count": execution.retry_count,
            "is_retry": execution.is_retry,
        }

        if exception:
            payload.update({
                "error_type": execution.error_type,
                "error_message": execution.error_message,
            })
        elif response:
            payload.update({
                "http_status_code": execution.http_status_code,
                "response_body": execution.http_response_body[:10000] if execution.http_response_body else None,
            })

        requests.post(f"{GATEWAY_URL}/callback", json=payload, timeout=5)
    except Exception as e:
        logger.warning("Failed to notify gateway: %s", e)
