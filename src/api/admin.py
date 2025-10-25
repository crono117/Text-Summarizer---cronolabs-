from django.contrib import admin
from .models import APIKey, APIRequestLog


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'is_active', 'created_at', 'last_used_at']
    list_filter = ['is_active', 'created_at', 'last_used_at']
    search_fields = ['user__username', 'user__email', 'name', 'key']
    readonly_fields = ['key', 'created_at', 'last_used_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Key Information', {
            'fields': ('user', 'name', 'key', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_used_at')
        }),
    )


@admin.register(APIRequestLog)
class APIRequestLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'endpoint', 'method', 'status_code', 'character_count', 'response_time_ms', 'timestamp']
    list_filter = ['endpoint', 'method', 'status_code', 'timestamp']
    search_fields = ['user__username', 'user__email', 'endpoint', 'error_message']
    readonly_fields = ['user', 'endpoint', 'method', 'status_code', 'character_count', 'response_time_ms', 'timestamp', 'error_message']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        # Logs are created automatically, not manually
        return False

    def has_change_permission(self, request, obj=None):
        # Logs are immutable
        return False
