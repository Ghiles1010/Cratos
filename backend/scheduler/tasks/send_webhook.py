import json
import logging
import uuid

import requests
from celery import shared_task
from django.db import transaction
from django.utils import timezone

from dataclasses import asdict

from apiauth.models import WebhookSigningKey
from scheduler.models import ExecutionStatus, FailureOutcome, FailureResult, SuccessResult, TaskExecution, TaskSchedule, TaskStatus
from scheduler.serializers import WebhookPayloadSerializer
from scheduler.domain.lifecycle.handler import TaskHandler
from scheduler.domain.execution.execution_recorder import ExecutionRecorder
from scheduler.utils.signing import sign

WEBHOOK_TIMEOUT = 30

logger = logging.getLogger(__name__)


@shared_task
def send_webhook(task_id: str):
    """Send HTTP POST to the task's callback_url and handle the outcome."""
    started_at = timezone.now()

    try:
        task = TaskSchedule.objects.select_related('user').get(task_id=uuid.UUID(task_id))
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

    if task.status == TaskStatus.PENDING:
        TaskHandler(task).begin_execution()
        task.save(update_fields=['status', 'started_at', 'updated_at'])

    try:
        payload_bytes = json.dumps(WebhookPayloadSerializer(task).data, separators=(',', ':')).encode()
        headers = {'Content-Type': 'application/json'}
        signing_key, _ = WebhookSigningKey.objects.get_or_create(
            user=task.user,
            defaults={'secret': WebhookSigningKey.generate_secret()},
        )
        headers.update(sign(payload_bytes, signing_key.secret))
        response = requests.post(task.callback_url, data=payload_bytes, headers=headers, timeout=WEBHOOK_TIMEOUT)
    except requests.RequestException as exc:
        _handle_exception(task, execution, exc)
        return

    if response.status_code in (200, 201, 202):
        _handle_success(task, execution, response)
    else:
        _handle_http_error(task, execution, response)


def _handle_success(task: TaskSchedule, execution: TaskExecution, response: requests.Response) -> None:
    ExecutionRecorder(execution).record_success(response)
    TaskHandler(task).complete()
    task.result = _success_result(task, response)
    task.save(update_fields=['status', 'result', 'last_run_at', 'run_count', 'retry_count', 'next_run_at', 'completed_at', 'updated_at'])
    logger.info("callback: task %s completed (run #%d), next_run_at=%s", task.task_id, task.run_count, task.next_run_at)


def _handle_exception(task: TaskSchedule, execution: TaskExecution, exc: Exception) -> None:
    ExecutionRecorder(execution).record_exception(exc)
    _fail_task(task, f"{type(exc).__name__}: {exc}")


def _handle_http_error(task: TaskSchedule, execution: TaskExecution, response: requests.Response) -> None:
    ExecutionRecorder(execution).record_http_error(response)
    _fail_task(task, f"HTTP {response.status_code}: {response.text[:500]}")


def _fail_task(task: TaskSchedule, error_detail: str) -> None:
    outcome = TaskHandler(task).fail()
    task.result = _failure_result(task, outcome, error_detail)
    task.save(update_fields=['status', 'result', 'completed_at', 'next_run_at', 'retry_count', 'updated_at'])
    if outcome.retried:
        logger.info("callback: task %s will be retried (%d/%d)", task.task_id, task.retry_count, task.max_retries)
    else:
        logger.warning("callback: task %s permanently failed", task.task_id)


def _success_result(task: TaskSchedule, response: requests.Response) -> dict:
    return asdict(SuccessResult(
        status_code=response.status_code,
        response_text=response.text[:1000],
        recurring_advanced=task.is_recurring,
    ))


def _failure_result(task: TaskSchedule, outcome: FailureOutcome, error_detail: str) -> dict:
    return asdict(FailureResult(
        error=error_detail,
        retry_count=task.retry_count,
        max_retries=task.max_retries,
        retry_policy=task.retry_policy,
        retry_scheduled=outcome.retried,
        retry_delay_seconds=outcome.retry_delay_seconds,
    ))
