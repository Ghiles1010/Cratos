"""URL patterns for the scheduler app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet

app_name = 'scheduler'

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='tasks')

urlpatterns = [
    path('', include(router.urls)),
]

