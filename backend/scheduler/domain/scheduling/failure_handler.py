from datetime import timedelta

from django.utils import timezone

from scheduler.models import FailureOutcome, RetryPolicy, TaskStatus


class FailureHandler:
    def __init__(self, task):
        self.task = task

    def handle(self) -> FailureOutcome:
        if self._should_retry():
            return self._reschedule()
        return self._mark_failed()

    def _should_retry(self) -> bool:
        if self.task.retry_policy == RetryPolicy.NONE:
            return False
        return self.task.retry_count < self.task.max_retries

    def _compute_delay(self) -> int:
        count = self.task.retry_count  # already incremented before this call
        base = self.task.retry_delay_seconds
        if self.task.retry_policy == RetryPolicy.FIXED:
            return base
        elif self.task.retry_policy == RetryPolicy.LINEAR:
            return base * count
        elif self.task.retry_policy == RetryPolicy.EXPONENTIAL:
            return base * (2 ** (count - 1))
        return base

    def _reschedule(self) -> FailureOutcome:
        self.task.retry_count += 1
        delay = self._compute_delay()
        self.task.next_run_at = timezone.now() + timedelta(seconds=delay)
        self.task.status = TaskStatus.SCHEDULED
        return FailureOutcome(retried=True, retry_delay_seconds=delay)

    def _mark_failed(self) -> FailureOutcome:
        self.task.status = TaskStatus.FAILED
        self.task.completed_at = timezone.now()
        self.task.next_run_at = None
        return FailureOutcome(retried=False)
