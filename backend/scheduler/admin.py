from django.contrib import admin
from django.utils import timezone

from .models import ExecutionStatus, TaskExecution, TaskSchedule, TaskStatus


@admin.register(TaskSchedule)
class TaskScheduleAdmin(admin.ModelAdmin):
    """Admin interface for TaskSchedule."""

    list_display = [
        'task_id', 'task_name', 'user', 'status', 'schedule_type',
        'next_run_at', 'run_count', 'is_paused', 'created_at',
        'execution_time_display',
    ]
    list_filter = ['status', 'schedule_type', 'is_paused', 'retry_policy', 'created_at', 'user']
    search_fields = ['task_id', 'task_name', 'user__username']
    readonly_fields = [
        'task_id', 'created_at', 'updated_at', 'started_at',
        'completed_at', 'execution_time', 'is_overdue',
        'next_run_at', 'last_run_at', 'run_count', 'retry_count',
    ]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Task Information', {
            'fields': ('task_id', 'task_name', 'task_args', 'task_kwargs', 'callback_url'),
        }),
        ('Scheduling', {
            'fields': (
                'schedule_type', 'schedule_time', 'cron_expression',
                'interval_seconds', 'ends_at', 'task_timezone',
                'next_run_at', 'last_run_at', 'run_count', 'is_paused',
            ),
        }),
        ('Retry Configuration', {
            'fields': ('retry_policy', 'max_retries', 'retry_delay_seconds', 'retry_count'),
        }),
        ('Status & Results', {
            'fields': ('status', 'result', 'user'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'started_at', 'completed_at'),
            'classes': ('collapse',),
        }),
    )

    def execution_time_display(self, obj):
        if obj.execution_time:
            return f"{obj.execution_time:.2f}s"
        return "—"
    execution_time_display.short_description = "Exec Time"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    actions = ['cancel_selected', 'pause_selected', 'resume_selected', 'retry_failed']

    def cancel_selected(self, request, queryset):
        count = queryset.filter(
            status__in=[TaskStatus.SCHEDULED, TaskStatus.PENDING],
        ).update(status=TaskStatus.CANCELLED, next_run_at=None)
        self.message_user(request, f"{count} task(s) cancelled.")
    cancel_selected.short_description = "Cancel selected tasks"

    def pause_selected(self, request, queryset):
        count = queryset.exclude(schedule_type='one_off').update(is_paused=True)
        self.message_user(request, f"{count} recurring task(s) paused.")
    pause_selected.short_description = "Pause selected recurring tasks"

    def resume_selected(self, request, queryset):
        count = 0
        for task in queryset.filter(is_paused=True):
            task.resume()
            count += 1
        self.message_user(request, f"{count} task(s) resumed.")
    resume_selected.short_description = "Resume selected tasks"

    def retry_failed(self, request, queryset):
        count = 0
        for task in queryset.filter(status=TaskStatus.FAILED):
            task.status = TaskStatus.SCHEDULED
            task.result = None
            task.retry_count = 0
            task.save()
            count += 1
        self.message_user(request, f"{count} failed task(s) re-queued.")
    retry_failed.short_description = "Retry failed tasks"


@admin.register(TaskExecution)
class TaskExecutionAdmin(admin.ModelAdmin):
    """Admin interface for TaskExecution."""

    list_display = [
        'id', 'task', 'execution_number', 'status', 'started_at',
        'duration_seconds', 'http_status_code', 'error_type',
    ]
    list_filter = ['status', 'is_retry', 'started_at']
    search_fields = ['task__task_id', 'task__task_name', 'error_message']
    readonly_fields = [
        'id', 'task', 'execution_number', 'status', 'started_at',
        'completed_at', 'duration_seconds', 'http_status_code',
        'http_response_body', 'http_response_headers', 'error_type',
        'error_message', 'error_traceback', 'retry_count', 'is_retry',
        'created_at',
    ]
    date_hierarchy = 'started_at'
    ordering = ['-started_at']

    fieldsets = (
        ('Execution Info', {
            'fields': ('task', 'execution_number', 'status', 'is_retry', 'retry_count'),
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'duration_seconds'),
        }),
        ('HTTP Response', {
            'fields': ('http_status_code', 'http_response_body', 'http_response_headers'),
            'classes': ('collapse',),
        }),
        ('Error Details', {
            'fields': ('error_type', 'error_message', 'error_traceback'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('task', 'task__user')
