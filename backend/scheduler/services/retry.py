"""
Retry orchestration for failed task callbacks.

Responsible for deciding *if* a task should be retried, computing
the delay, and rescheduling it.  Does not perform the HTTP call itself.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils import timezone

from .scheduling import compute_retry_delay, should_retry

if TYPE_CHECKING:
    from ..models import TaskSchedule

logger = logging.getLogger(__name__)


def handle_failure(task: "TaskSchedule", error_detail: str) -> bool:
    """
    Handle a callback failure.

    Returns ``True`` if the task was rescheduled for retry,
    ``False`` if it has been permanently marked as failed.
    """
    from ..models import TaskStatus

    if should_retry(task):
        return _reschedule_for_retry(task, error_detail)

    _mark_permanently_failed(task, error_detail)
    return False


def _reschedule_for_retry(task: "TaskSchedule", error_detail: str) -> bool:
    """Bump retry_count, compute delay, set next_run_at."""
    task.retry_count += 1
    delay = compute_retry_delay(
        task.retry_policy,
        task.retry_count - 1,  # 0-based for delay calculation
        task.retry_delay_seconds,
    )

    task.next_run_at = timezone.now() + timezone.timedelta(seconds=delay)
    task.status = "scheduled"
    task.result = _build_result(task, error_detail, retry_scheduled=True, delay=delay)

    task.save(update_fields=[
        'retry_count', 'next_run_at', 'status', 'result', 'updated_at',
    ])

    logger.info(
        "Task %s scheduled for retry %d/%d in %ds",
        task.task_id, task.retry_count, task.max_retries, delay,
    )
    return True


def _mark_permanently_failed(task: "TaskSchedule", error_detail: str) -> None:
    """
    No more retries — mark as failed (dead letter queue).
    
    Tasks that exceed max_retries are marked as FAILED and will not
    be automatically retried. They can be manually retried via the API/UI.
    """
    from ..models import TaskStatus

    task.status = TaskStatus.FAILED
    task.completed_at = timezone.now()
    task.next_run_at = None
    task.result = _build_result(task, error_detail, retry_scheduled=False)
    # Mark as permanently failed in result
    if isinstance(task.result, dict):
        task.result['permanently_failed'] = True
        task.result['failed_at'] = timezone.now().isoformat()

    task.save(update_fields=[
        'status', 'completed_at', 'next_run_at', 'result', 'updated_at',
    ])

    logger.warning(
        "Task %s permanently failed after %d retries (dead letter queue)",
        task.task_id, task.retry_count,
    )


def _build_result(
    task: "TaskSchedule",
    error_detail: str,
    *,
    retry_scheduled: bool,
    delay: int | None = None,
) -> dict:
    """Build the result payload persisted on the task."""
    result = task.result if isinstance(task.result, dict) else {}
    result.update({
        'error': error_detail,
        'retry_count': task.retry_count,
        'max_retries': task.max_retries,
        'retry_policy': task.retry_policy,
        'retry_scheduled': retry_scheduled,
    })
    if delay is not None:
        result['retry_delay_seconds'] = delay
    return result

