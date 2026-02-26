import ipaddress
from urllib.parse import urlparse

from django.utils import timezone
from rest_framework import serializers

from .models import ExecutionStatus, RetryPolicy, ScheduleType, TaskExecution, TaskSchedule
from .utils.cron_parser import describe_cron, validate_cron


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
            'status', 'result',
            # meta
            'user', 'created_at', 'updated_at',
            'started_at', 'completed_at',
            # computed
            'execution_time', 'is_overdue', 'is_recurring', 'scheduler_info',
            'execution_history',
        ]
        read_only_fields = [
            'task_id', 'user', 'status', 'result',
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
                'error_type': e.error_type,
                'error_message': e.error_message,
                'retry_count': e.retry_count,
                'is_retry': e.is_retry,
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
        parsed = urlparse(value)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname:
            raise serializers.ValidationError("Must be a valid HTTP/HTTPS URL.")
        
        # Allow private IPs in DEBUG mode for local development
        from django.conf import settings
        if settings.DEBUG:
            return value
        
        hostname = parsed.hostname.lower()
        if hostname in ('localhost', '127.0.0.1', '::1'):
            raise serializers.ValidationError("Cannot use localhost or loopback addresses.")
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_unspecified:
                raise serializers.ValidationError("Cannot use private/loopback IPs.")
        except ValueError:
            if hostname.endswith(('.local', '.internal', '.private', '.corp')):
                raise serializers.ValidationError("Cannot use internal domains.")
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

        if schedule_type == ScheduleType.CRON and not attrs.get('cron_expression'):
            raise serializers.ValidationError({
                'cron_expression': "Required for cron schedule type.",
            })
        if schedule_type == ScheduleType.INTERVAL and not attrs.get('interval_seconds'):
            raise serializers.ValidationError({
                'interval_seconds': "Required for interval schedule type.",
            })

        # Retry validation
        policy = attrs.get('retry_policy', RetryPolicy.NONE)
        max_r = attrs.get('max_retries', 0)
        if policy != RetryPolicy.NONE and max_r == 0:
            raise serializers.ValidationError({
                'max_retries': "Must be > 0 when a retry policy is set.",
            })

        return attrs
