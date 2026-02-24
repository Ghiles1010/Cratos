from django.utils import timezone

from .base import TaskState
from scheduler.models.enums import TaskStatus
from scheduler.domain.scheduling.next_run import NextRunComputer
from scheduler.domain.scheduling.failure import FailureHandler
from scheduler.models import FailureOutcome


class RunningState(TaskState):
    status = TaskStatus.RUNNING

    def complete(self):
        now = timezone.now()
        self.task.run_count += 1
        self.task.retry_count = 0
        self.task.last_run_at = now

        if not self.task.is_recurring:
            self._transition(TaskStatus.COMPLETED)
            self.task.completed_at = now
            self.task.next_run_at = None
            return

        if self.task.ends_at and now >= self.task.ends_at:
            self._transition(TaskStatus.COMPLETED)
            self.task.next_run_at = None
            return

        next_run = NextRunComputer(self.task).compute()
        if next_run is None:
            self._transition(TaskStatus.COMPLETED)
            self.task.next_run_at = None
        else:
            self._transition(TaskStatus.SCHEDULED)
            self.task.next_run_at = next_run

    def fail(self) -> FailureOutcome:
        return FailureHandler(self.task).handle()
