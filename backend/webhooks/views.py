from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import AllowedOrigin, WebhookSigningKey
from .serializers import AllowedOriginSerializer, WebhookSigningKeySerializer


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def signing_key_view(request):
    """GET → return current signing secret.  POST → rotate to a new one."""
    obj, _ = WebhookSigningKey.objects.get_or_create(
        user=request.user,
        defaults={'secret': WebhookSigningKey.generate_secret()},
    )
    if request.method == 'POST':
        obj.rotate()
        serializer = WebhookSigningKeySerializer(obj, context={'rotated': True})
    else:
        serializer = WebhookSigningKeySerializer(obj)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def allowed_origins_view(request):
    """GET → list allowed origins.  POST → add a new one."""
    if request.method == 'POST':
        serializer = AllowedOriginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    origins = AllowedOrigin.objects.all().order_by('scheme', 'host', 'port')
    return Response(AllowedOriginSerializer(origins, many=True).data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def allowed_origin_detail_view(request, pk):
    """DELETE → remove an allowed origin."""
    try:
        origin = AllowedOrigin.objects.get(pk=pk)
    except AllowedOrigin.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    origin.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
