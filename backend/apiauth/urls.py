from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_key_view, name='api-key'),
    path('token/', views.api_key_token_view, name='api-key-token'),
    path('webhook-secret/', views.webhook_signing_key_view, name='webhook-signing-key'),
]

