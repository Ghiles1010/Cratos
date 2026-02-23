from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_key_view, name='api-key'),
]

