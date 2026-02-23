"""Task views for the standalone scheduler."""

from typing import Callable
from typing import Any

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import TaskSchedule, TaskStatus
from .serializers import TaskScheduleSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """Full CRUD + pause/resume/retry for scheduled tasks."""

    serializer_class = TaskScheduleSerializer
    lookup_field = 'task_id'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TaskSchedule.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def _perform_task_action(self, action: Callable[[TaskSchedule], Any]) -> Response:
        task = self.get_object()
        try:
            action(task)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(task).data, status=status.HTTP_200_OK)

    # ── Custom actions ───────────────────────────────────────────────────

    @action(detail=False, methods=['get'], url_path='scheduled')
    def list_scheduled(self, request):
        queryset = (
            self.get_queryset()
            .filter(status=TaskStatus.SCHEDULED)
            .order_by('next_run_at', 'created_at')
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_task(self, request, task_id=None):
        return self._perform_task_action(TaskSchedule.cancel)

    @action(detail=True, methods=['post'], url_path='pause')
    def pause_task(self, request, task_id=None):
        return self._perform_task_action(TaskSchedule.pause)

    @action(detail=True, methods=['post'], url_path='resume')
    def resume_task(self, request, task_id=None):
        return self._perform_task_action(TaskSchedule.resume)

    @action(detail=True, methods=['post'], url_path='retry')
    def retry_task(self, request, task_id=None):
        return self._perform_task_action(TaskSchedule.retry)
