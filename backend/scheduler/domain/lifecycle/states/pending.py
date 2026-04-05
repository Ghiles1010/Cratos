from django.utils import timezone
from .base import TaskState
from scheduler.models.enums import TaskStatus

class PendingState(TaskState):
    status = TaskStatus.PENDING

    def begin_execution(self):
        self._transition(TaskStatus.RUNNING)
        self.task.started_at = timezone.now()

    def cancel(self):
        self._transition(TaskStatus.CANCELLED)