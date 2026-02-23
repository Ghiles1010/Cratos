"""Task views for the standalone scheduler."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import TaskSchedule, TaskStatus
from .serializers import TaskScheduleSerializer
from .services.scheduling import compute_next_run


class TaskViewSet(viewsets.ModelViewSet):
    """Full CRUD + pause/resume/retry for scheduled tasks."""

    serializer_class = TaskScheduleSerializer
    lookup_field = 'task_id'
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TaskSchedule.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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
        task = self.get_object()
        task.cancel()
        return Response(self.get_serializer(task).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='pause')
    def pause_task(self, request, task_id=None):
        task = self.get_object()
        if not task.is_recurring:
            return Response(
                {'detail': 'Only recurring tasks can be paused.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        task.pause()
        return Response(self.get_serializer(task).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='resume')
    def resume_task(self, request, task_id=None):
        task = self.get_object()
        if not task.is_recurring:
            return Response(
                {'detail': 'Only recurring tasks can be resumed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        task.resume()
        return Response(self.get_serializer(task).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='retry')
    def retry_task(self, request, task_id=None):
        task = self.get_object()
        if task.status != TaskStatus.FAILED:
            return Response(
                {'detail': 'Only failed tasks can be retried.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        task.status = TaskStatus.SCHEDULED
        task.retry_count = 0
        task.result = None
        task.completed_at = None
        task.next_run_at = compute_next_run(task)
        task.save(update_fields=[
            'status', 'retry_count', 'result', 'completed_at',
            'next_run_at', 'updated_at',
        ])
        return Response(self.get_serializer(task).data, status=status.HTTP_200_OK)

