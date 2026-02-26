from django.contrib import admin
from .models import APIKey, WebhookSigningKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'label', 'key_preview', 'created_at', 'last_used']
    readonly_fields = ['key', 'created_at', 'last_used']
    search_fields = ['user__username', 'user__email', 'label']

    def key_preview(self, obj):
        return f'{obj.key[:8]}…' if obj.key else '—'
    key_preview.short_description = 'Key'


@admin.register(WebhookSigningKey)
class WebhookSigningKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'secret_preview', 'created_at', 'last_rotated_at']
    readonly_fields = ['secret', 'created_at', 'last_rotated_at']
    search_fields = ['user__username', 'user__email']

    def secret_preview(self, obj):
        return f'{obj.secret[:14]}…' if obj.secret else '—'
    secret_preview.short_description = 'Secret'

