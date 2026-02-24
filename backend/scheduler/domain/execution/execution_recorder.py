import traceback

import requests
from django.utils import timezone

from scheduler.models import ExecutionStatus, TaskExecution


class ExecutionRecorder:
    def __init__(self, execution: TaskExecution):
        self.execution = execution

    def record_success(self, response: requests.Response) -> None:
        self.execution.status = ExecutionStatus.SUCCESS
        self.execution.completed_at = timezone.now()
        self._apply_response(response)
        self.execution.save()

    def record_exception(self, exc: Exception) -> None:
        self.execution.status = ExecutionStatus.FAILED
        self.execution.completed_at = timezone.now()
        self.execution.error_type = type(exc).__name__
        self.execution.error_message = str(exc)
        self.execution.error_traceback = ''.join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )[:20000]
        self.execution.save()

    def record_http_error(self, response: requests.Response) -> None:
        self.execution.status = ExecutionStatus.FAILED
        self.execution.completed_at = timezone.now()
        self.execution.error_type = "HTTPError"
        self.execution.error_message = f"HTTP {response.status_code}: {response.text[:500]}"
        self._apply_response(response)
        self.execution.save()

    def _apply_response(self, response: requests.Response) -> None:
        self.execution.http_status_code = response.status_code
        self.execution.http_response_body = response.text[:10000]
        self.execution.http_response_headers = dict(response.headers)
