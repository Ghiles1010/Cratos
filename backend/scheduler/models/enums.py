from django.db import models


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


class ExecutionStatus(models.TextChoices):
    """Status of a single task execution."""
    PENDING = 'pending', 'Pending'
    RUNNING = 'running', 'Running'
    SUCCESS = 'success', 'Success'
    FAILED = 'failed', 'Failed'
    TIMEOUT = 'timeout', 'Timeout'
