from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import APIKey, WebhookSigningKey


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_key_view(request):
    """GET → return current key.  POST → regenerate."""
    api_key, created = APIKey.objects.get_or_create(
        user=request.user,
        defaults={'key': APIKey.generate_key()},
    )
    if request.method == 'POST':
        new_key = api_key.regenerate()
        return Response({'key': new_key, 'regenerated': True})
    return Response({'key': api_key.key})


@api_view(['POST'])
@permission_classes([AllowAny])
def api_key_token_view(request):
    """POST {username, password} → return the user's API key."""
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')

    if not username or not password:
        return Response(
            {'error': 'username and password are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    api_key, _ = APIKey.objects.get_or_create(
        user=user,
        defaults={'key': APIKey.generate_key()},
    )
    return Response({'key': api_key.key})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def webhook_signing_key_view(request):
    """GET → return current signing secret.  POST → rotate to a new one."""
    obj, _ = WebhookSigningKey.objects.get_or_create(
        user=request.user,
        defaults={'secret': WebhookSigningKey.generate_secret()},
    )
    if request.method == 'POST':
        new_secret = obj.rotate()
        return Response({'secret': new_secret, 'rotated': True})
    return Response({'secret': obj.secret})
