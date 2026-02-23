from django.utils import timezone

from ..models import TaskSchedule


def build_payload(task: TaskSchedule) -> dict:
    return {
        'task_id': str(task.task_id),
        'task_name': task.task_name,
        'task_args': task.task_args,
        'task_kwargs': task.task_kwargs,
        'schedule_time': task.schedule_time.isoformat() if task.schedule_time else None,
        'status': task.status,
        'run_count': task.run_count,
        'is_recurring': task.is_recurring,
        'timestamp': timezone.now().isoformat(),
        'message': 'Task execution triggered',
    }
