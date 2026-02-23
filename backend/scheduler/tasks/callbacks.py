"""
Callback executor — sends the HTTP POST to the task's callback_url
and updates status accordingly.

Retry logic is delegated to ``scheduler.services.retry``.
Recurring advancement is delegated to ``scheduler.services.scheduling``.
"""

import logging
import traceback
import uuid
import os

import requests
from celery import shared_task
from django.db import transaction
from django.utils import timezone

from ..models import ExecutionStatus, TaskExecution, TaskSchedule, TaskStatus
from ..services.retry import handle_failure
from ..services.scheduling import advance_recurring

logger = logging.getLogger(__name__)

# Timeout for callback HTTP requests (seconds).
CALLBACK_TIMEOUT = 30

# WebSocket Gateway URL (optional - if not set, WebSocket notifications are disabled)
GATEWAY_URL = os.getenv("WEBSOCKET_GATEWAY_URL", None)


@shared_task(bind=True)
def send_callback_notification(self, task_id: str):
    """Send HTTP POST to the task's callback_url and handle the outcome."""
    execution = None
    started_at = timezone.now()

    try:
        task = TaskSchedule.objects.get(task_id=uuid.UUID(task_id))
    except (TaskSchedule.DoesNotExist, ValueError):
        logger.error("callback: task %s not found — skipping", task_id)
        return

    # Guard: only process pending/running tasks
    if task.status not in (TaskStatus.PENDING, TaskStatus.RUNNING):
        logger.warning("callback: task %s has status %s — skipping", task_id, task.status)
        return

    # Create execution record
    with transaction.atomic():
        # Get next execution number
        last_exec = (
            TaskExecution.objects.filter(task=task)
            .order_by('-execution_number')
            .first()
        )
        exec_number = (last_exec.execution_number + 1) if last_exec else 1

        execution = TaskExecution.objects.create(
            task=task,
            execution_number=exec_number,
            status=ExecutionStatus.RUNNING,
            started_at=started_at,
            retry_count=task.retry_count,
            is_retry=task.retry_count > 0,
        )

    # Mark as running
    if task.status != TaskStatus.RUNNING:
        task.status = TaskStatus.RUNNING
        task.save(update_fields=['status', 'updated_at'])

    payload = _build_payload(task)

    # Execute the callback (HTTP POST to callback_url)
    try:
        response = requests.post(
            task.callback_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=CALLBACK_TIMEOUT,
        )
    except requests.RequestException as exc:
        _handle_error(task, execution, exc, None)
        return

    # Handle outcome (updates execution status, advances recurring tasks, etc.)
    if response.status_code in (200, 201, 202):
        _handle_success(task, execution, response)
    else:
        _handle_error(task, execution, None, response)


# ── Gateway integration ──────────────────────────────────────────────────────

def _send_to_gateway(task: TaskSchedule, execution: TaskExecution, response, exception):
    """Send execution result to WebSocket gateway for real-time notifications."""
    if not GATEWAY_URL:
        return
    
    try:
        gateway_payload = {
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
            gateway_payload.update({
                "error_type": execution.error_type,
                "error_message": execution.error_message,
            })
        elif response:
            gateway_payload.update({
                "http_status_code": execution.http_status_code,
                "response_body": execution.http_response_body[:10000] if execution.http_response_body else None,
            })
        
        requests.post(
            f"{GATEWAY_URL}/callback",
            json=gateway_payload,
            timeout=5,
        )
    except Exception as e:
        logger.warning(f"Failed to notify gateway: {e}")


# ── Outcome handlers ────────────────────────────────────────────────────────

def _handle_success(
    task: TaskSchedule,
    execution: TaskExecution,
    response: requests.Response,
) -> None:
    """Mark the task as completed and advance recurring schedule if needed."""
    completed_at = timezone.now()

    # Update execution record
    execution.status = ExecutionStatus.SUCCESS
    execution.completed_at = completed_at
    if response:
        execution.http_status_code = response.status_code
        execution.http_response_body = response.text[:10000]
        execution.http_response_headers = dict(response.headers)
    execution.save()

    # Notify gateway (non-blocking, for WebSocket subscribers)
    if GATEWAY_URL:
        try:
            _send_to_gateway(task, execution, response, None)
        except Exception as e:
            logger.warning(f"Gateway notification failed (non-critical): {e}")

    task.result = {
        'status_code': response.status_code,
        'response_text': response.text[:1000],
    }

    if task.is_recurring:
        advance_recurring(task)
        task.result['recurring_advanced'] = True
        task.save(update_fields=[
            'status', 'result', 'last_run_at', 'run_count',
            'retry_count', 'next_run_at', 'updated_at',
        ])
        logger.info(
            "callback: task %s completed (run #%d), next_run_at=%s",
            task.task_id, task.run_count, task.next_run_at,
        )
    else:
        task.status = TaskStatus.COMPLETED
        task.completed_at = completed_at
        task.run_count += 1
        task.next_run_at = None
        task.save(update_fields=[
            'status', 'result', 'completed_at', 'run_count',
            'next_run_at', 'updated_at',
        ])
        logger.info("callback: task %s completed", task.task_id)


def _handle_error(
    task: TaskSchedule,
    execution: TaskExecution,
    exception: Exception | None,
    response: requests.Response | None,
) -> None:
    """Record error in execution and delegate to retry service."""
    completed_at = timezone.now()
    error_detail = ""

    if exception:
        error_type = type(exception).__name__
        error_message = str(exception)
        error_traceback = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        error_detail = f"{error_type}: {error_message}"
    elif response:
        error_type = "HTTPError"
        error_message = f"HTTP {response.status_code}: {response.text[:500]}"
        error_traceback = None
        error_detail = error_message
    else:
        error_type = "UnknownError"
        error_message = "Unknown error"
        error_traceback = None
        error_detail = error_message

    # Update execution record
    execution.status = ExecutionStatus.FAILED
    execution.completed_at = completed_at
    execution.error_type = error_type
    execution.error_message = error_message
    if error_traceback:
        execution.error_traceback = error_traceback[:20000]
    if response:
        execution.http_status_code = response.status_code
        execution.http_response_body = response.text[:10000]
        execution.http_response_headers = dict(response.headers)
    execution.save()

    # Notify gateway (non-blocking, for WebSocket subscribers)
    if GATEWAY_URL:
        try:
            _send_to_gateway(task, execution, response, exception)
        except Exception as e:
            logger.warning(f"Gateway notification failed (non-critical): {e}")

    # Delegate to retry service
    retried = handle_failure(task, error_detail)
    if retried:
        logger.info("callback: task %s will be retried", task.task_id)
    else:
        logger.warning("callback: task %s permanently failed", task.task_id)


# ── Payload builder ──────────────────────────────────────────────────────────

def _build_payload(task: TaskSchedule) -> dict:
    return {
        'task_id': str(task.task_id),
        'task_name': task.task_name,
        'task_args': task.task_args,
        'task_kwargs': task.task_kwargs,
        'schedule_time': task.schedule_time.isoformat() if task.schedule_time else None,
        'status': task.status,
        'run_count': task.run_count,
        'is_recurring': task.is_recurring,
        'timestamp': timezone.now().isoformat(),
        'message': 'Task execution triggered',
    }
