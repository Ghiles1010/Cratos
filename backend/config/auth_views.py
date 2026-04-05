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


# ── Change password ───────────────────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Change the current user's password.

    ```json
    { "current_password": "old", "new_password": "new" }
    ```
    """
    current = request.data.get("current_password", "")
    new = request.data.get("new_password", "")

    if not current or not new:
        return Response({"detail": "current_password and new_password are required."}, status=400)
    if len(new) < 8:
        return Response({"detail": "new_password must be at least 8 characters."}, status=400)
    if not request.user.check_password(current):
        return Response({"detail": "current_password is incorrect."}, status=400)

    request.user.set_password(new)
    request.user.save(update_fields=["password"])
    return Response({"detail": "Password changed successfully."})


# ── Change username ───────────────────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_username_view(request):
    """
    Change the current user's username. Requires password confirmation.

    ```json
    { "password": "current", "new_username": "alice" }
    ```
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    password = request.data.get("password", "")
    new_username = request.data.get("new_username", "").strip()

    if not password or not new_username:
        return Response({"detail": "password and new_username are required."}, status=400)
    if not request.user.check_password(password):
        return Response({"detail": "password is incorrect."}, status=400)
    if User.objects.filter(username=new_username).exclude(pk=request.user.pk).exists():
        return Response({"detail": "Username already taken."}, status=400)

    request.user.username = new_username
    request.user.save(update_fields=["username"])
    return Response({"detail": "Username changed successfully.", "username": new_username})

