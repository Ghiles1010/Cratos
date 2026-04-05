from .base import TaskState
from scheduler.models.enums import TaskStatus


class FailedState(TaskState):
    status = TaskStatus.FAILED

    def retry(self):
        self._transition(TaskStatus.SCHEDULED)
        self.task.retry_count = 0
        self.task.completed_at = None

    def cancel(self):
        self._transition(TaskStatus.CANCELLED)