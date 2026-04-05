from scheduler.models import FailureOutcome
from .states.factory import build_state


class TaskHandler:
    def __init__(self, task):
        self.task = task

    def _state(self):
        # Always resolve the current state dynamically
        return build_state(self.task)

    # ── Dispatcher Phase ─────────────────────────────

    def claim(self):
        self._state().claim()

    # ── Worker Phase ────────────────────────────────

    def begin_execution(self):
        self._state().begin_execution()

    # ── Terminal Transitions ─────────────────────────

    def complete(self):
        self._state().complete()

    def fail(self) -> FailureOutcome:
        return self._state().fail()

    def cancel(self):
        self._state().cancel()

    def retry(self):
        self._state().retry()

    # ── Pause flag (not a status transition) ─────────

    def pause(self):
        if not self.task.is_pausable:
            raise ValueError(f"Cannot pause a {self.task.schedule_type} task in {self.task.status} status")
        self.task.is_paused = True

    def resume(self):
        if not self.task.is_paused:
            raise ValueError("Task is not paused")
        self.task.is_paused = False