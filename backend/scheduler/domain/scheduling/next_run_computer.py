from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from django.utils import timezone

from scheduler.utils.cron_parser import next_cron_occurrence

if TYPE_CHECKING:
    from scheduler.models import TaskSchedule

logger = logging.getLogger(__name__)


class NextRunComputer:
    def __init__(self, task: "TaskSchedule"):
        self.task = task

    def compute(self) -> Optional[datetime]:
        """Return the next UTC datetime this task should fire, or None."""
        from scheduler.models import ScheduleType, TaskStatus

        if self.task.status == TaskStatus.CANCELLED:
            return None
        if self.task.is_paused:
            return None

        if self.task.schedule_type == ScheduleType.ONE_OFF:
            return self._one_off()
        elif self.task.schedule_type == ScheduleType.CRON:
            return self._cron()
        elif self.task.schedule_type == ScheduleType.INTERVAL:
            return self._interval()

        return None

    def _one_off(self) -> Optional[datetime]:
        from scheduler.models import TaskStatus

        if self.task.run_count > 0:
            return None
        if self.task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
            return None
        return self.task.schedule_time or timezone.now()

    def _cron(self) -> Optional[datetime]:
        if not self.task.cron_expression:
            return None

        reference = self.task.last_run_at or self.task.schedule_time or timezone.now()
        try:
            return next_cron_occurrence(
                self.task.cron_expression,
                after=reference,
                tz_name=self.task.task_timezone,
            )
        except ValueError as exc:
            logger.warning("Invalid cron expression %r: %s", self.task.cron_expression, exc)
            return None

    def _interval(self) -> Optional[datetime]:
        if not self.task.interval_seconds:
            return None

        base = self.task.last_run_at or self.task.schedule_time or timezone.now()
        return base + timedelta(seconds=self.task.interval_seconds)
