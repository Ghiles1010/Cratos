"""
Central dispatcher — periodically scans for due tasks and enqueues callbacks.

Uses ``next_run_at`` as the single source of truth for "is this task due?",
which supports one-off, cron, and interval schedules uniformly.
"""

import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from ..models import TaskSchedule, TaskStatus
from ..domain.lifecycle.handler import TaskHandler
from .send_webhook import send_webhook

logger = logging.getLogger(__name__)


@shared_task
def dispatch_due_tasks(batch_size: int = 100):
    """
    Claim due tasks (next_run_at <= now, status=scheduled, not paused)
    and fan-out ``send_webhook`` jobs.
    """
    now = timezone.now()
    claimed_ids: list[str] = []

    logger.info("dispatcher: scanning for tasks due before %s", now.isoformat())

    try:
        with transaction.atomic():
            due_tasks = (
                TaskSchedule.objects
                .select_for_update(skip_locked=True)
                .filter(
                    next_run_at__lte=now,
                    status=TaskStatus.SCHEDULED,
                    is_paused=False,
                )
                .order_by('next_run_at')[:batch_size]
            )

            for task in due_tasks:
                TaskHandler(task).claim()
                task.save(update_fields=['status', 'updated_at'])
                claimed_ids.append(str(task.task_id))

        # Enqueue callbacks outside the transaction
        for task_id in claimed_ids:
            send_webhook.delay(task_id)

        if claimed_ids:
            preview = claimed_ids[:10]
            suffix = "…" if len(claimed_ids) > 10 else ""
            logger.info(
                "dispatcher: dispatched %d tasks — %s%s",
                len(claimed_ids), preview, suffix,
            )
        else:
            logger.debug("dispatcher: no due tasks")

    except Exception:
        logger.exception("dispatcher: error during scan")
        raise
