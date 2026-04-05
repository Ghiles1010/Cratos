from rest_framework import authentication, exceptions
from .models import APIKey


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Authenticate requests via ``Authorization: Api-Key <key>`` header.
    """

    keyword = 'Api-Key'

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith(f'{self.keyword} '):
            return None

        raw_key = auth_header[len(self.keyword) + 1:].strip()
        if not raw_key:
            return None

        try:
            api_key = APIKey.objects.select_related('user').get(key=raw_key)
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API key.')

        if not api_key.user.is_active:
            raise exceptions.AuthenticationFailed('User account is disabled.')

        api_key.touch()
        return (api_key.user, api_key)

    def authenticate_header(self, request):
        return self.keyword

