from django.db import models

from .enums import ExecutionStatus
from .task_schedule import TaskSchedule


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

    # Result
    result = models.JSONField(null=True, blank=True)

    # Retry info
    retry_count = models.PositiveIntegerField(default=0)
    is_retry = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cratos_task_execution'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['task', '-started_at'], name='cratos_texec_task_start_idx'),
            models.Index(fields=['status', '-started_at'], name='cratos_texec_status_idx'),
            models.Index(fields=['started_at'], name='cratos_texec_started_idx'),
        ]
        unique_together = [['task', 'execution_number']]

    def __str__(self):
        return f"{self.task.task_name} execution #{self.execution_number} - {self.status}"

    def save(self, *args, **kwargs):
        if self.started_at and self.completed_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        super().save(*args, **kwargs)
