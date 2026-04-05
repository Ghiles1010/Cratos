"""
State machine: TaskHandler transitions (no DB needed – SimpleNamespace stands in
for the model since states only read/write plain attributes).
"""
from types import SimpleNamespace

from django.test import SimpleTestCase

from scheduler.domain.lifecycle.handler import TaskHandler
from scheduler.models.enums import RetryPolicy, ScheduleType, TaskStatus


def _task(**kw):
    defaults = dict(
        status=TaskStatus.SCHEDULED,
        schedule_type=ScheduleType.ONE_OFF,
        is_paused=False,
        is_recurring=False,  # property on the model; set explicitly here
        is_pausable=False,
        run_count=0,
        retry_count=0,
        max_retries=0,
        retry_policy=RetryPolicy.NONE,
        retry_delay_seconds=60,
        next_run_at=None,
        schedule_time=None,
        last_run_at=None,
        ends_at=None,
        completed_at=None,
        started_at=None,
    )
    defaults.update(kw)
    return SimpleNamespace(**defaults)


class TaskHandlerTransitionsTest(SimpleTestCase):

    def test_claim_moves_to_pending(self):
        task = _task()
        TaskHandler(task).claim()
        self.assertEqual(task.status, TaskStatus.PENDING)

    def test_begin_execution_moves_to_running(self):
        task = _task(status=TaskStatus.PENDING)
        TaskHandler(task).begin_execution()
        self.assertEqual(task.status, TaskStatus.RUNNING)

    def test_complete_one_off_moves_to_completed(self):
        task = _task(status=TaskStatus.RUNNING, is_recurring=False)
        TaskHandler(task).complete()
        self.assertEqual(task.status, TaskStatus.COMPLETED)

    def test_retry_resets_failed_to_scheduled(self):
        task = _task(status=TaskStatus.FAILED, retry_count=2)
        TaskHandler(task).retry()
        self.assertEqual(task.status, TaskStatus.SCHEDULED)
        self.assertEqual(task.retry_count, 0)  # retry() resets the counter

    def test_completed_task_rejects_all_transitions(self):
        for action in ("cancel", "retry", "claim"):
            with self.subTest(action=action):
                task = _task(status=TaskStatus.COMPLETED)
                with self.assertRaises(ValueError):
                    getattr(TaskHandler(task), action)()
