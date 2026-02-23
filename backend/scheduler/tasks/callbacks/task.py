import json
import logging
import uuid

import requests
from celery import shared_task
from django.db import transaction
from django.utils import timezone

from ..models import ExecutionStatus, TaskExecution, TaskSchedule, TaskStatus
from . import handlers
from .payload import build_payload
from ...services.signing import sign

logger = logging.getLogger(__name__)

CALLBACK_TIMEOUT = 30


@shared_task(bind=True)
def send_callback_notification(self, task_id: str):
    """Send HTTP POST to the task's callback_url and handle the outcome."""
    started_at = timezone.now()

    try:
        task = TaskSchedule.objects.get(task_id=uuid.UUID(task_id))
    except (TaskSchedule.DoesNotExist, ValueError):
        logger.error("callback: task %s not found — skipping", task_id)
        return

    if task.status not in (TaskStatus.PENDING, TaskStatus.RUNNING):
        logger.warning("callback: task %s has status %s — skipping", task_id, task.status)
        return

    with transaction.atomic():
        last_exec = TaskExecution.objects.filter(task=task).order_by('-execution_number').first()
        exec_number = (last_exec.execution_number + 1) if last_exec else 1
        execution = TaskExecution.objects.create(
            task=task,
            execution_number=exec_number,
            status=ExecutionStatus.RUNNING,
            started_at=started_at,
            retry_count=task.retry_count,
            is_retry=task.retry_count > 0,
        )

    if task.status != TaskStatus.RUNNING:
        task.status = TaskStatus.RUNNING
        task.save(update_fields=['status', 'updated_at'])

    payload = build_payload(task)
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode()

    headers = {'Content-Type': 'application/json'}
    if task.webhook_secret:
        headers.update(sign(payload_bytes, task.webhook_secret))

    try:
        response = requests.post(
            task.callback_url,
            data=payload_bytes,
            headers=headers,
            timeout=CALLBACK_TIMEOUT,
        )
    except requests.RequestException as exc:
        handlers.handle_error(task, execution, exc, None)
        return

    if response.status_code in (200, 201, 202):
        handlers.handle_success(task, execution, response)
    else:
        handlers.handle_error(task, execution, None, response)
