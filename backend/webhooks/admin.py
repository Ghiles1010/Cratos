from django.contrib import admin

from .models import AllowedOrigin, WebhookSigningKey


@admin.register(AllowedOrigin)
class AllowedOriginAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'scheme', 'host', 'port']
    list_filter = ['scheme']
    search_fields = ['host']


@admin.register(WebhookSigningKey)
class WebhookSigningKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'secret_preview', 'created_at', 'last_rotated_at']
    readonly_fields = ['secret', 'created_at', 'last_rotated_at']
    search_fields = ['user__username', 'user__email']

    def secret_preview(self, obj):
        return f'{obj.secret[:14]}…' if obj.secret else '—'
    secret_preview.short_description = 'Secret'
