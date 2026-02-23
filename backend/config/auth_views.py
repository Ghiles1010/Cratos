"""
Session-based authentication views for the Scheduler UI.

Follows the Elasticsearch/Kibana pattern:
  - The *service* owns auth (session + API-key)
  - The *UI* delegates to the service via session cookies
  - API keys remain available for programmatic / SDK access
"""
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json


# ── CSRF token endpoint (SPA reads the cookie) ──────────────────────────────
@ensure_csrf_cookie
@require_GET
def csrf_token_view(request):
    """Return the CSRF token so the SPA can store it for subsequent POSTs."""
    return JsonResponse({"csrfToken": get_token(request)})


# ── Login ────────────────────────────────────────────────────────────────────
@csrf_exempt          # Login is the entry-point; no CSRF token available yet
@require_POST
def login_view(request):
    """Authenticate with username + password, set a session cookie."""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    username = body.get("username", "").strip()
    password = body.get("password", "")

    if not username or not password:
        return JsonResponse({"error": "username and password are required"}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    if not user.is_active:
        return JsonResponse({"error": "Account is disabled"}, status=403)

    login(request, user)
    return JsonResponse({
        "user": {
            "id": user.pk,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
        }
    })


# ── Logout ───────────────────────────────────────────────────────────────────
@require_POST
def logout_view(request):
    """Destroy the current session."""
    logout(request)
    return JsonResponse({"detail": "Logged out"})


# ── Current user (session-protected) ────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Return the currently authenticated user's profile."""
    user = request.user
    return Response({
        "id": user.pk,
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
    })

