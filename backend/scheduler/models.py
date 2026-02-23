import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class TaskStatus(models.TextChoices):
    SCHEDULED = 'scheduled', 'Scheduled'
    PENDING = 'pending', 'Pending'
    RUNNING = 'running', 'Running'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'


class ScheduleType(models.TextChoices):
    ONE_OFF = 'one_off', 'One-off'
    CRON = 'cron', 'Cron'
    INTERVAL = 'interval', 'Interval'


class RetryPolicy(models.TextChoices):
    NONE = 'none', 'No retries'
    FIXED = 'fixed', 'Fixed delay'
    EXPONENTIAL = 'exponential', 'Exponential backoff'
    LINEAR = 'linear', 'Linear backoff'


class TaskSchedule(models.Model):
    """Model for storing scheduled tasks."""

    # Primary key
    task_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # ── Task details ─────────────────────────────────────────────────────
    task_name = models.CharField(max_length=255, help_text="Name of the task to execute")
    task_args = models.JSONField(default=list, help_text="Positional arguments for the task")
    task_kwargs = models.JSONField(default=dict, help_text="Keyword arguments for the task")
    callback_url = models.URLField(
        blank=True, null=True,
        help_text="URL to POST to when task execution is triggered (optional if using WebSocket gateway)"
    )

    # ── Scheduling ───────────────────────────────────────────────────────
    schedule_type = models.CharField(
        max_length=20,
        choices=ScheduleType.choices,
        default=ScheduleType.ONE_OFF,
        help_text="Type of schedule: one-off, cron, or interval",
    )
    schedule_time = models.DateTimeField(
        null=True, blank=True,
        help_text="When to execute (one-off) or first execution (recurring)",
    )
    cron_expression = models.CharField(
        max_length=100, blank=True, default='',
        help_text="Cron expression, e.g. '*/5 * * * *' (minute hour day month weekday)",
    )
    interval_seconds = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Repeat every N seconds (interval schedule)",
    )
    ends_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Stop recurring execution after this time",
    )
    task_timezone = models.CharField(
        max_length=63, default='UTC',
        help_text="IANA timezone for schedule interpretation, e.g. 'America/New_York'",
    )
    next_run_at = models.DateTimeField(
        null=True, blank=True, db_index=True,
        help_text="Next calculated execution time (UTC). Managed by the system.",
    )
    last_run_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Last time this task was dispatched",
    )
    run_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this task has been dispatched",
    )
    is_paused = models.BooleanField(
        default=False,
        help_text="Pause recurring task without deleting it",
    )

    # ── Retry configuration ──────────────────────────────────────────────
    retry_policy = models.CharField(
        max_length=20,
        choices=RetryPolicy.choices,
        default=RetryPolicy.NONE,
        help_text="Retry strategy on callback failure",
    )
    max_retries = models.PositiveIntegerField(
        default=0,
        help_text="Maximum number of retry attempts (0 = no retries)",
    )
    retry_delay_seconds = models.PositiveIntegerField(
        default=60,
        help_text="Base delay between retries in seconds",
    )
    retry_count = models.PositiveIntegerField(
        default=0,
        help_text="Current retry attempt number",
    )

    # ── Status / results ─────────────────────────────────────────────────
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.SCHEDULED)
    result = models.JSONField(null=True, blank=True, help_text="Task execution result or error")

    # ── Metadata ─────────────────────────────────────────────────────────
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='task_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'orkera_task_schedule'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'schedule_time']),
            models.Index(fields=['created_at']),
            models.Index(fields=['next_run_at', 'status']),
        ]

    def __str__(self):
        return f"{self.task_name} ({self.task_id}) - {self.status}"

    # ── Lifecycle ────────────────────────────────────────────────────────

    def save(self, *args, **kwargs):
        from .services.scheduling import compute_next_run  # avoid circular

        is_new = self._state.adding

        # Default schedule_time to now for immediate one-off tasks
        if is_new and self.callback_url and not self.schedule_time:
            self.schedule_time = timezone.now()

        # Compute next_run_at when creating or when relevant fields change
        if is_new or not kwargs.get('update_fields'):
            self.next_run_at = compute_next_run(self)

        # Auto-set timestamps based on status
        if self.status == TaskStatus.RUNNING and not self.started_at:
            self.started_at = timezone.now()
        elif self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED) and not self.completed_at:
            self.completed_at = timezone.now()

        super().save(*args, **kwargs)

    def cancel(self):
        """Mark the task as cancelled."""
        if self.status not in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
            self.status = TaskStatus.CANCELLED
            self.next_run_at = None
            self.save(update_fields=['status', 'next_run_at', 'updated_at'])

    def pause(self):
        """Pause a recurring task."""
        if self.schedule_type != ScheduleType.ONE_OFF:
            self.is_paused = True
            self.save(update_fields=['is_paused', 'updated_at'])

    def resume(self):
        """Resume a paused recurring task."""
        from .services.scheduling import compute_next_run

        if self.is_paused:
            self.is_paused = False
            self.status = TaskStatus.SCHEDULED
            self.next_run_at = compute_next_run(self)
            self.save(update_fields=['is_paused', 'status', 'next_run_at', 'updated_at'])

    # ── Properties ───────────────────────────────────────────────────────

    @property
    def is_recurring(self):
        return self.schedule_type != ScheduleType.ONE_OFF

    @property
    def is_overdue(self):
        if self.next_run_at and self.status == TaskStatus.SCHEDULED:
            return timezone.now() > self.next_run_at
        return False

    @property
    def execution_time(self):
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class ExecutionStatus(models.TextChoices):
    """Status of a single task execution."""
    PENDING = 'pending', 'Pending'
    RUNNING = 'running', 'Running'
    SUCCESS = 'success', 'Success'
    FAILED = 'failed', 'Failed'
    TIMEOUT = 'timeout', 'Timeout'


class TaskExecution(models.Model):
    """
    Execution history for a task.
    
    Each time a task is dispatched and executed, a TaskExecution record
    is created to track the outcome, duration, errors, and response details.
    """

    id = models.BigAutoField(primary_key=True)
    task = models.ForeignKey(
        TaskSchedule,
        on_delete=models.CASCADE,
        related_name='executions',
        db_index=True,
    )
    execution_number = models.PositiveIntegerField(
        help_text="Sequential execution number for this task (1, 2, 3, ...)",
    )
    status = models.CharField(
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PENDING,
    )
    started_at = models.DateTimeField(db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)

    # HTTP response details
    http_status_code = models.IntegerField(null=True, blank=True)
    http_response_body = models.TextField(null=True, blank=True, max_length=10000)
    http_response_headers = models.JSONField(null=True, blank=True)

    # Error details
    error_message = models.TextField(null=True, blank=True, max_length=5000)
    error_type = models.CharField(max_length=255, null=True, blank=True)
    error_traceback = models.TextField(null=True, blank=True, max_length=20000)

    # Retry info
    retry_count = models.PositiveIntegerField(default=0)
    is_retry = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orkera_task_execution'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['task', '-started_at']),
            models.Index(fields=['status', '-started_at']),
            models.Index(fields=['started_at']),
        ]
        unique_together = [['task', 'execution_number']]

    def __str__(self):
        return f"{self.task.task_name} execution #{self.execution_number} - {self.status}"

    def save(self, *args, **kwargs):
        # Calculate duration if both timestamps are set
        if self.started_at and self.completed_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        super().save(*args, **kwargs)
