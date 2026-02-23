import logging
import traceback

import requests
from django.utils import timezone

from ..models import ExecutionStatus, TaskExecution, TaskSchedule, TaskStatus
from ..services.retry import handle_failure
from ..services.scheduling import advance_recurring
from . import gateway

logger = logging.getLogger(__name__)


def handle_success(task: TaskSchedule, execution: TaskExecution, response: requests.Response) -> None:
    completed_at = timezone.now()

    execution.status = ExecutionStatus.SUCCESS
    execution.completed_at = completed_at
    execution.http_status_code = response.status_code
    execution.http_response_body = response.text[:10000]
    execution.http_response_headers = dict(response.headers)
    execution.save()

    gateway.notify(task, execution, response, None)

    task.result = {
        'status_code': response.status_code,
        'response_text': response.text[:1000],
    }

    if task.is_recurring:
        advance_recurring(task)
        task.result['recurring_advanced'] = True
        task.save(update_fields=['status', 'result', 'last_run_at', 'run_count', 'retry_count', 'next_run_at', 'updated_at'])
        logger.info("callback: task %s completed (run #%d), next_run_at=%s", task.task_id, task.run_count, task.next_run_at)
    else:
        task.status = TaskStatus.COMPLETED
        task.completed_at = completed_at
        task.run_count += 1
        task.next_run_at = None
        task.save(update_fields=['status', 'result', 'completed_at', 'run_count', 'next_run_at', 'updated_at'])
        logger.info("callback: task %s completed", task.task_id)


def handle_error(
    task: TaskSchedule,
    execution: TaskExecution,
    exception: Exception | None,
    response: requests.Response | None,
) -> None:
    completed_at = timezone.now()

    if exception:
        error_type = type(exception).__name__
        error_message = str(exception)
        error_traceback = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        error_detail = f"{error_type}: {error_message}"
    elif response:
        error_type = "HTTPError"
        error_message = f"HTTP {response.status_code}: {response.text[:500]}"
        error_traceback = None
        error_detail = error_message
    else:
        error_type = "UnknownError"
        error_message = "Unknown error"
        error_traceback = None
        error_detail = error_message

    execution.status = ExecutionStatus.FAILED
    execution.completed_at = completed_at
    execution.error_type = error_type
    execution.error_message = error_message
    if error_traceback:
        execution.error_traceback = error_traceback[:20000]
    if response:
        execution.http_status_code = response.status_code
        execution.http_response_body = response.text[:10000]
        execution.http_response_headers = dict(response.headers)
    execution.save()

    gateway.notify(task, execution, response, exception)

    retried = handle_failure(task, error_detail)
    if retried:
        logger.info("callback: task %s will be retried", task.task_id)
    else:
        logger.warning("callback: task %s permanently failed", task.task_id)
