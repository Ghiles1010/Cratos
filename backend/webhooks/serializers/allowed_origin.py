from rest_framework import serializers

from webhooks.models import AllowedOrigin


class AllowedOriginSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowedOrigin
        fields = ['id', 'scheme', 'host', 'port']
