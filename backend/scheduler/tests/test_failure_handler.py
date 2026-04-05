"""
FailureHandler: retry delay math and exhaustion logic (no DB needed).
"""
from types import SimpleNamespace

from django.test import SimpleTestCase

from scheduler.domain.scheduling.failure_handler import FailureHandler
from scheduler.models.enums import RetryPolicy, TaskStatus


def _task(**kw):
    defaults = dict(
        retry_policy=RetryPolicy.FIXED,
        retry_count=2,   # before handler runs
        max_retries=5,
        retry_delay_seconds=60,
        status=TaskStatus.RUNNING,
        next_run_at=None,
        completed_at=None,
    )
    defaults.update(kw)
    return SimpleNamespace(**defaults)


class FailureHandlerDelayTest(SimpleTestCase):

    def test_fixed_delay_is_always_the_base(self):
        task = _task(retry_policy=RetryPolicy.FIXED, retry_count=2, retry_delay_seconds=60)
        outcome = FailureHandler(task).handle()
        self.assertTrue(outcome.retried)
        self.assertEqual(outcome.retry_delay_seconds, 60)

    def test_linear_delay_scales_with_retry_count(self):
        # retry_count goes 2 → 3; LINEAR delay = base * count = 60 * 3 = 180
        task = _task(retry_policy=RetryPolicy.LINEAR, retry_count=2, retry_delay_seconds=60)
        outcome = FailureHandler(task).handle()
        self.assertEqual(outcome.retry_delay_seconds, 180)

    def test_exponential_delay_doubles_each_retry(self):
        # retry_count goes 2 → 3; EXPONENTIAL delay = base * 2^(count-1) = 60 * 4 = 240
        task = _task(retry_policy=RetryPolicy.EXPONENTIAL, retry_count=2, retry_delay_seconds=60)
        outcome = FailureHandler(task).handle()
        self.assertEqual(outcome.retry_delay_seconds, 240)

    def test_exhausted_retries_marks_task_failed(self):
        task = _task(retry_policy=RetryPolicy.FIXED, retry_count=3, max_retries=3)
        outcome = FailureHandler(task).handle()
        self.assertFalse(outcome.retried)
        self.assertEqual(task.status, TaskStatus.FAILED)
        self.assertIsNone(task.next_run_at)
