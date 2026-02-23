"""
Pure scheduling logic — no Django ORM side-effects.

All functions accept model instances or plain values and return
datetimes.  This keeps the service easy to unit-test and under 200 lines.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from django.utils import timezone

from .cron_parser import next_cron_occurrence

if TYPE_CHECKING:
    from ..models import TaskSchedule

logger = logging.getLogger(__name__)


# ── Public API ───────────────────────────────────────────────────────────────

def compute_next_run(task: "TaskSchedule") -> Optional[datetime]:
    """Return the next UTC datetime this task should fire, or *None*."""
    from ..models import ScheduleType, TaskStatus

    if task.status in (TaskStatus.CANCELLED,):
        return None
    if task.is_paused:
        return None

    if task.schedule_type == ScheduleType.ONE_OFF:
        return _next_run_one_off(task)
    elif task.schedule_type == ScheduleType.CRON:
        return _next_run_cron(task)
    elif task.schedule_type == ScheduleType.INTERVAL:
        return _next_run_interval(task)

    return None


def compute_retry_delay(
    retry_policy: str,
    retry_count: int,
    base_delay: int,
) -> int:
    """Return the delay in seconds before the next retry attempt."""
    from ..models import RetryPolicy

    if retry_policy == RetryPolicy.FIXED:
        return base_delay
    elif retry_policy == RetryPolicy.LINEAR:
        return base_delay * (retry_count + 1)
    elif retry_policy == RetryPolicy.EXPONENTIAL:
        return base_delay * (2 ** retry_count)
    return base_delay


def should_retry(task: "TaskSchedule") -> bool:
    """Return True if the task should be retried after a failure."""
    from ..models import RetryPolicy

    if task.retry_policy == RetryPolicy.NONE:
        return False
    return task.retry_count < task.max_retries


def advance_recurring(task: "TaskSchedule") -> None:
    """
    After a successful dispatch, advance the recurring task for its next run.

    Mutates *task* in-place but does NOT call save().
    The caller is responsible for persisting changes.
    """
    from ..models import ScheduleType, TaskStatus

    if task.schedule_type == ScheduleType.ONE_OFF:
        return

    task.last_run_at = timezone.now()
    task.run_count += 1
    task.retry_count = 0  # reset retries for new run

    # Check end time
    if task.ends_at and timezone.now() >= task.ends_at:
        task.status = TaskStatus.COMPLETED
        task.next_run_at = None
        return

    # Compute next run
    next_run = compute_next_run(task)
    if next_run is None:
        task.status = TaskStatus.COMPLETED
        task.next_run_at = None
    else:
        task.next_run_at = next_run
        task.status = TaskStatus.SCHEDULED


# ── Private helpers ──────────────────────────────────────────────────────────

def _next_run_one_off(task: "TaskSchedule") -> Optional[datetime]:
    """One-off: just use the schedule_time (or now)."""
    from ..models import TaskStatus

    # Already executed
    if task.run_count > 0:
        return None
    if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
        return None
    return task.schedule_time or timezone.now()


def _next_run_cron(task: "TaskSchedule") -> Optional[datetime]:
    """Cron: parse expression and find next occurrence."""
    if not task.cron_expression:
        return None

    reference = task.last_run_at or task.schedule_time or timezone.now()
    try:
        return next_cron_occurrence(
            task.cron_expression,
            after=reference,
            tz_name=task.task_timezone,
        )
    except ValueError as exc:
        logger.warning("Invalid cron expression %r: %s", task.cron_expression, exc)
        return None


def _next_run_interval(task: "TaskSchedule") -> Optional[datetime]:
    """Interval: last_run + interval_seconds."""
    if not task.interval_seconds:
        return None

    base = task.last_run_at or task.schedule_time or timezone.now()
    return base + timedelta(seconds=task.interval_seconds)

