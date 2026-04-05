from django.urls import path

from . import views

urlpatterns = [
    path('signing-key/', views.signing_key_view, name='webhook-signing-key'),
    path('allowed-origins/', views.allowed_origins_view, name='webhook-allowed-origins'),
    path('allowed-origins/<int:pk>/', views.allowed_origin_detail_view, name='webhook-allowed-origin-detail'),
]
