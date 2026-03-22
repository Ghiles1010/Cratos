from django.utils import timezone
from rest_framework import serializers

from .models import ExecutionStatus, RetryPolicy, ScheduleType, TaskExecution, TaskSchedule
from .utils.cron_parser import describe_cron, validate_cron
from webhooks.services.errors import URLPolicyError
from webhooks.services.origin_checker import OriginChecker


class WebhookPayloadSerializer(serializers.ModelSerializer):
    task_id = serializers.UUIDField()
    is_recurring = serializers.ReadOnlyField()
    timestamp = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    class Meta:
        model = TaskSchedule
        fields = [
            'task_id', 'task_name', 'task_args', 'task_kwargs',
            'schedule_time', 'status', 'run_count', 'is_recurring',
            'timestamp', 'message',
        ]

    def get_timestamp(self, obj):
        return timezone.now().isoformat()

    def get_message(self, obj):
        return 'Task execution triggered'


class TaskScheduleSerializer(serializers.ModelSerializer):
    """
    Represents a scheduled task.

    ## Schedule types

    Set `schedule_type` to one of:

    - **`one_off`** — runs once. Provide `schedule_time` (ISO 8601 UTC) or omit to run immediately.
      - Required: *(none beyond the common fields)*
      - Optional: `schedule_time`, `task_timezone`
      - Forbidden: `cron_expression`, `interval_seconds`

    - **`cron`** — recurring on a cron schedule. Provide a standard 5-field cron expression.
      - Required: `cron_expression`
      - Optional: `task_timezone`, `ends_at`
      - Forbidden: `schedule_time`, `interval_seconds`

    - **`interval`** — recurring every N seconds.
      - Required: `interval_seconds` (positive integer)
      - Optional: `ends_at`
      - Forbidden: `schedule_time`, `cron_expression`

    ## Retry policies

    Set `retry_policy` to one of `none` (default), `fixed`, `linear`, `exponential`.
    When using any retry policy other than `none`, `max_retries` must be > 0.

    ## Webhook delivery

    Cratos will POST to `callback_url` with the task payload and an HMAC-SHA256
    signature header (`X-Cratos-Signature`) for verification.
    """

    task_id = serializers.UUIDField(read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    execution_time = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    is_recurring = serializers.ReadOnlyField()
    scheduler_info = serializers.SerializerMethodField()
    execution_history = serializers.SerializerMethodField()

    class Meta:
        model = TaskSchedule
        fields = [
            # identity
            'task_id', 'task_name', 'task_args', 'task_kwargs', 'callback_url',
            # scheduling
            'schedule_type', 'schedule_time', 'cron_expression',
            'interval_seconds', 'ends_at', 'task_timezone',
            'next_run_at', 'last_run_at', 'run_count', 'is_paused',
            # retry
            'retry_policy', 'max_retries', 'retry_delay_seconds', 'retry_count',
            # status
            'status',
            # meta
            'user', 'created_at', 'updated_at',
            'started_at', 'completed_at',
            # computed
            'execution_time', 'is_overdue', 'is_recurring', 'scheduler_info',
            'execution_history',
        ]
        read_only_fields = [
            'task_id', 'user', 'status',
            'created_at', 'updated_at', 'started_at', 'completed_at',
            'next_run_at', 'last_run_at', 'run_count', 'retry_count',
            'execution_time', 'is_overdue', 'is_recurring', 'scheduler_info',
            'execution_history',
        ]

    # ── Scheduler info ───────────────────────────────────────────────────

    def get_scheduler_info(self, obj):
        info = {
            'schedule_type': obj.schedule_type,
            'is_recurring': obj.is_recurring,
            'is_paused': obj.is_paused,
            'status': obj.status,
            'run_count': obj.run_count,
            'next_run_at': obj.next_run_at,
        }
        if obj.schedule_type == ScheduleType.CRON:
            info['cron_expression'] = obj.cron_expression
            info['cron_description'] = describe_cron(obj.cron_expression)
        elif obj.schedule_type == ScheduleType.INTERVAL:
            info['interval_seconds'] = obj.interval_seconds
        if obj.retry_policy != RetryPolicy.NONE:
            info['retry_policy'] = obj.retry_policy
            info['max_retries'] = obj.max_retries
            info['retry_count'] = obj.retry_count
        return info

    def get_execution_history(self, obj):
        """Return recent execution history (last 20 executions)."""
        executions = (
            TaskExecution.objects
            .filter(task=obj)
            .order_by('-started_at')[:20]
        )
        return [
            {
                'execution_number': e.execution_number,
                'status': e.status,
                'started_at': e.started_at.isoformat() if e.started_at else None,
                'completed_at': e.completed_at.isoformat() if e.completed_at else None,
                'duration_seconds': e.duration_seconds,
                'http_status_code': e.http_status_code,
                'http_response_body': e.http_response_body,
                'error_type': e.error_type,
                'error_message': e.error_message,
                'retry_count': e.retry_count,
                'is_retry': e.is_retry,
                'result': e.result,
            }
            for e in executions
        ]

    # ── Validators ───────────────────────────────────────────────────────

    def validate_schedule_time(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("Schedule time must be in the future.")
        return value

    def validate_callback_url(self, value):
        if not value:
            raise serializers.ValidationError("Callback URL is required.")
        try:
            OriginChecker().check_url(value)
        except URLPolicyError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def validate_cron_expression(self, value):
        if not value:
            return value
        try:
            validate_cron(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def validate_task_timezone(self, value):
        import zoneinfo
        try:
            zoneinfo.ZoneInfo(value)
        except (KeyError, Exception):
            raise serializers.ValidationError(f"Invalid timezone: {value!r}")
        return value

    def validate(self, attrs):
        schedule_type = attrs.get('schedule_type', ScheduleType.ONE_OFF)
        errors = {}

        if schedule_type == ScheduleType.ONE_OFF:
            if attrs.get('cron_expression'):
                errors['cron_expression'] = "Not used for one_off tasks. Remove it or set schedule_type to 'cron'."
            if attrs.get('interval_seconds'):
                errors['interval_seconds'] = "Not used for one_off tasks. Remove it or set schedule_type to 'interval'."

        elif schedule_type == ScheduleType.CRON:
            if not attrs.get('cron_expression'):
                errors['cron_expression'] = "Required for cron tasks. Example: '0 9 * * 1-5' (weekdays at 9am)."
            if attrs.get('schedule_time'):
                errors['schedule_time'] = "Not used for cron tasks. Remove it or set schedule_type to 'one_off'."
            if attrs.get('interval_seconds'):
                errors['interval_seconds'] = "Not used for cron tasks. Remove it or set schedule_type to 'interval'."

        elif schedule_type == ScheduleType.INTERVAL:
            if not attrs.get('interval_seconds'):
                errors['interval_seconds'] = "Required for interval tasks. Provide a positive integer (seconds)."
            if attrs.get('schedule_time'):
                errors['schedule_time'] = "Not used for interval tasks. Remove it or set schedule_type to 'one_off'."
            if attrs.get('cron_expression'):
                errors['cron_expression'] = "Not used for interval tasks. Remove it or set schedule_type to 'cron'."

        if errors:
            raise serializers.ValidationError(errors)

        # Retry validation
        policy = attrs.get('retry_policy', RetryPolicy.NONE)
        if policy != RetryPolicy.NONE and not attrs.get('max_retries'):
            raise serializers.ValidationError({
                'max_retries': "Must be > 0 when retry_policy is set. Example: max_retries=3.",
            })

        return attrs
