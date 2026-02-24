from .base import TaskState
from scheduler.models.enums import TaskStatus


class CancelledState(TaskState):
    status = TaskStatus.CANCELLED