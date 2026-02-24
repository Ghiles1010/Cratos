from django.utils import timezone
from .base import TaskState
from scheduler.models.enums import TaskStatus


class ScheduledState(TaskState):
    status = TaskStatus.SCHEDULED

    def claim(self):
        self._transition(TaskStatus.PENDING)

    def cancel(self):
        self._transition(TaskStatus.CANCELLED)
        self.task.next_run_at = None