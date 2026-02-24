from scheduler.models.enums import TaskStatus
from scheduler.domain.lifecycle.states.scheduled import ScheduledState
from scheduler.domain.lifecycle.states.pending import PendingState
from scheduler.domain.lifecycle.states.running import RunningState
from scheduler.domain.lifecycle.states.failed import FailedState
from scheduler.domain.lifecycle.states.completed import CompletedState
from scheduler.domain.lifecycle.states.cancelled import CancelledState


STATE_MAP = {
    TaskStatus.SCHEDULED: ScheduledState,
    TaskStatus.PENDING: PendingState,
    TaskStatus.RUNNING: RunningState,
    TaskStatus.FAILED: FailedState,
    TaskStatus.COMPLETED: CompletedState,
    TaskStatus.CANCELLED: CancelledState,
}


def build_state(task):
    state_cls = STATE_MAP.get(task.status)
    if not state_cls:
        raise ValueError(f"Unknown status: {task.status}")
    return state_cls(task)