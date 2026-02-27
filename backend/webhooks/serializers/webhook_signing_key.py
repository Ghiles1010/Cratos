from rest_framework import serializers

from webhooks.models import WebhookSigningKey


class WebhookSigningKeySerializer(serializers.ModelSerializer):
    rotated = serializers.SerializerMethodField()

    class Meta:
        model = WebhookSigningKey
        fields = ['secret', 'created_at', 'last_rotated_at', 'rotated']
        read_only_fields = ['secret', 'created_at', 'last_rotated_at']

    def get_rotated(self, obj) -> bool:
        return self.context.get('rotated', False)
