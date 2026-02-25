import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone

from .enums import RetryPolicy, ScheduleType, TaskStatus


class TaskSchedule(models.Model):
    """Persistent representation of a scheduled task."""

    # ── Identity ──────────────────────────────────────────────────────────

    task_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # ── Task payload ──────────────────────────────────────────────────────

    task_name = models.CharField(max_length=255)
    task_args = models.JSONField(default=list)
    task_kwargs = models.JSONField(default=dict)

    callback_url = models.URLField(blank=True, null=True)
    webhook_secret = models.CharField(max_length=255, blank=True, default="")

    # ── Scheduling configuration ──────────────────────────────────────────

    schedule_type = models.CharField(
        max_length=20,
        choices=ScheduleType.choices,
        default=ScheduleType.ONE_OFF,
    )

    schedule_time = models.DateTimeField(null=True, blank=True)
    cron_expression = models.CharField(max_length=100, blank=True, default="")
    interval_seconds = models.PositiveIntegerField(null=True, blank=True)

    ends_at = models.DateTimeField(null=True, blank=True)
    task_timezone = models.CharField(max_length=63, default="UTC")

    # ── Runtime tracking ──────────────────────────────────────────────────

    next_run_at = models.DateTimeField(null=True, db_index=True)
    last_run_at = models.DateTimeField(null=True, blank=True)

    run_count = models.PositiveIntegerField(default=0)
    retry_count = models.PositiveIntegerField(default=0)

    retry_policy = models.CharField(
        max_length=20,
        choices=RetryPolicy.choices,
        default=RetryPolicy.NONE,
    )

    max_retries = models.PositiveIntegerField(default=0)
    retry_delay_seconds = models.PositiveIntegerField(default=60)

    is_paused = models.BooleanField(default=False)

    # ── Lifecycle ─────────────────────────────────────────────────────────

    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.SCHEDULED,
    )

    result = models.JSONField(null=True, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # ── Ownership / metadata ─────────────────────────────────────────────

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="task_schedules",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ── Meta ──────────────────────────────────────────────────────────────

    class Meta:
        db_table = "orkera_task_schedule"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["next_run_at", "status"]),
        ]

    # ── Derived Properties ────────────────────────────────────────────────

    @property
    def is_recurring(self) -> bool:
        return self.schedule_type != ScheduleType.ONE_OFF

    @property
    def is_pausable(self) -> bool:
        return self.is_recurring and self.status == TaskStatus.SCHEDULED

    @property
    def is_overdue(self) -> bool:
        if self.next_run_at and self.status == TaskStatus.SCHEDULED:
            return timezone.now() > self.next_run_at
        return False

    @property
    def execution_time(self):
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def __str__(self):
        return f"{self.task_name} ({self.task_id}) - {self.status}"