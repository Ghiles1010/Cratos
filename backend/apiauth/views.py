from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import APIKey


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

