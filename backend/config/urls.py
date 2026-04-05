"""URL configuration for the standalone Scheduler service."""

from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from apiauth.authentication import APIKeyAuthentication

from scheduler.models import TaskSchedule, TaskStatus, TaskExecution, ExecutionStatus


def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'scheduler'})


@api_view(['GET'])
@authentication_classes([SessionAuthentication, APIKeyAuthentication])
@permission_classes([IsAuthenticated])
def metrics(request):
    """Prometheus metrics endpoint (for external scrapers)."""
    from django.db.models import Count, Avg

    now = timezone.now()

    # Task counts by status
    status_counts = dict(
        TaskSchedule.objects.values('status')
        .annotate(count=Count('task_id'))
        .values_list('status', 'count')
    )

    # Execution counts
    execution_counts = dict(
        TaskExecution.objects.values('status')
        .annotate(count=Count('id'))
        .values_list('status', 'count')
    )

    # Overdue tasks
    overdue = TaskSchedule.objects.filter(
        next_run_at__lte=now,
        status=TaskStatus.SCHEDULED,
        is_paused=False,
    ).count()

    # Average execution duration (last 100 successful executions)
    avg_duration = (
        TaskExecution.objects.filter(
            status=ExecutionStatus.SUCCESS,
            duration_seconds__isnull=False,
        )
        .order_by('-started_at')[:100]
        .aggregate(avg=Avg('duration_seconds'))['avg']
        or 0.0
    )

    lines = [
        '# HELP scheduler_tasks_total Total number of tasks by status',
        '# TYPE scheduler_tasks_total gauge',
    ]
    for status in TaskStatus.values:
        count = status_counts.get(status, 0)
        lines.append(f'scheduler_tasks_total{{status="{status}"}} {count}')

    lines.extend(
        [
            '',
            '# HELP scheduler_executions_total Total number of task executions by status',
            '# TYPE scheduler_executions_total counter',
        ]
    )
    for status in ExecutionStatus.values:
        count = execution_counts.get(status, 0)
        lines.append(f'scheduler_executions_total{{status="{status}"}} {count}')

    lines.extend(
        [
            '',
            '# HELP scheduler_overdue_tasks_count Number of overdue tasks',
            '# TYPE scheduler_overdue_tasks_count gauge',
            f'scheduler_overdue_tasks_count {overdue}',
            '',
            '# HELP scheduler_task_execution_duration_seconds Average task execution duration',
            '# TYPE scheduler_task_execution_duration_seconds gauge',
            f'scheduler_task_execution_duration_seconds {avg_duration:.3f}',
        ]
    )

    return HttpResponse('\n'.join(lines), content_type='text/plain; version=0.0.4')


@api_view(['GET'])
@authentication_classes([SessionAuthentication, APIKeyAuthentication])
@permission_classes([IsAuthenticated])
def metrics_json(request):
    """
    JSON metrics endpoint for the built-in UI dashboard.
    Returns a structured summary instead of Prometheus text format.
    """
    from django.db.models import Count, Avg

    now = timezone.now()

    status_counts = dict(
        TaskSchedule.objects.values('status')
        .annotate(count=Count('task_id'))
        .values_list('status', 'count')
    )

    execution_counts = dict(
        TaskExecution.objects.values('status')
        .annotate(count=Count('id'))
        .values_list('status', 'count')
    )

    overdue = TaskSchedule.objects.filter(
        next_run_at__lte=now,
        status=TaskStatus.SCHEDULED,
        is_paused=False,
    ).count()

    avg_duration = (
        TaskExecution.objects.filter(
            status=ExecutionStatus.SUCCESS,
            duration_seconds__isnull=False,
        )
        .order_by('-started_at')[:100]
        .aggregate(avg=Avg('duration_seconds'))['avg']
        or 0.0
    )

    # Recent executions (last 50)
    recent_qs = (
        TaskExecution.objects.select_related('task')
        .order_by('-started_at')[:50]
        .only(
            'status',
            'started_at',
            'completed_at',
            'duration_seconds',
            'retry_count',
            'is_retry',
            'task__task_id',
            'task__task_name',
        )
    )
    recent_executions = [
        {
            'task_id': str(exec.task.task_id),
            'task_name': exec.task.task_name,
            'status': exec.status,
            'started_at': exec.started_at,
            'completed_at': exec.completed_at,
            'duration_seconds': exec.duration_seconds,
            'retry_count': exec.retry_count,
            'is_retry': exec.is_retry,
        }
        for exec in recent_qs
    ]

    payload = {
        'generated_at': now,
        'tasks_by_status': status_counts,
        'executions_by_status': execution_counts,
        'overdue_tasks': overdue,
        'avg_execution_duration_seconds': avg_duration,
        'recent_executions': recent_executions,
    }

    return JsonResponse(payload, safe=False)


urlpatterns = [
    path('api/', include('scheduler.urls')),
    path('api/keys/', include('apiauth.urls')),
    path('api/webhooks/', include('webhooks.urls')),
    path('api/auth/', include('config.auth_urls')),
    path('health/', health_check, name='health-check'),
    path('metrics/', metrics, name='metrics'),
    path('metrics/json/', metrics_json, name='metrics-json'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
