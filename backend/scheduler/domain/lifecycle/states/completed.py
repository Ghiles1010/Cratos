from .base import TaskState
from scheduler.models.enums import TaskStatus


class CompletedState(TaskState):
    status = TaskStatus.COMPLETED