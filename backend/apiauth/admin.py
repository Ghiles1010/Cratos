from django.contrib import admin
from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'label', 'key_preview', 'created_at', 'last_used']
    readonly_fields = ['key', 'created_at', 'last_used']
    search_fields = ['user__username', 'user__email', 'label']

    def key_preview(self, obj):
        return f'{obj.key[:8]}…' if obj.key else '—'
    key_preview.short_description = 'Key'

