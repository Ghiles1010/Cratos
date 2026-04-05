from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import TaskSchedule
from .serializers import TaskScheduleSerializer
from scheduler.domain.lifecycle.handler import TaskHandler
from django_filters.rest_framework import DjangoFilterBackend

class TaskViewSet(viewsets.ModelViewSet):

    serializer_class = TaskScheduleSerializer
    lookup_field = "task_id"
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        qs = (
            TaskSchedule.objects
            .filter(user=self.request.user)
            .order_by("next_run_at", "created_at")
        )
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(task_name__icontains=search)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ── Helper ─────────────────────────────

    def _handle(self, transition_callable):
        task = self.get_object()
        handler = TaskHandler(task)

        try:
            transition_callable(handler)
            task.save()
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            self.get_serializer(task).data,
            status=status.HTTP_200_OK,
        )

    # ── Custom actions ─────────────────────

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, *args, **kwargs):
        return self._handle(lambda h: h.cancel())

    @action(detail=True, methods=["post"], url_path="retry")
    def retry(self, *args, **kwargs):
        return self._handle(lambda h: h.retry())

    @action(detail=True, methods=["post"], url_path="pause")
    def pause(self, *args, **kwargs):
        return self._handle(lambda h: h.pause())

    @action(detail=True, methods=["post"], url_path="resume")
    def resume(self, *args, **kwargs):
        return self._handle(lambda h: h.resume())