from abc import ABC
from scheduler.models import FailureOutcome, TaskStatus



class TaskState(ABC):
    status: TaskStatus

    def __init__(self, task):
        self.task = task

    def _transition(self, new_status: TaskStatus):
        self.task.status = new_status

    # Dispatcher phase
    def claim(self):
        raise ValueError(f"Cannot claim from {self.status}")

    # Worker execution phase
    def begin_execution(self):
        raise ValueError(f"Cannot begin execution from {self.status}")

    def complete(self):
        raise ValueError(f"Cannot complete from {self.status}")

    def fail(self) -> FailureOutcome:
        raise ValueError(f"Cannot fail from {self.status}")

    def cancel(self):
        raise ValueError(f"Cannot cancel from {self.status}")

    def retry(self):
        raise ValueError(f"Cannot retry from {self.status}")