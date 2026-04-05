"""Authentication URL patterns for the Scheduler UI."""

from django.urls import path
from . import auth_views

urlpatterns = [
    path('csrf/',            auth_views.csrf_token_view,      name='auth-csrf'),
    path('login/',           auth_views.login_view,           name='auth-login'),
    path('logout/',          auth_views.logout_view,          name='auth-logout'),
    path('me/',              auth_views.me_view,              name='auth-me'),
    path('change-password/', auth_views.change_password_view, name='auth-change-password'),
    path('change-username/', auth_views.change_username_view, name='auth-change-username'),
]
