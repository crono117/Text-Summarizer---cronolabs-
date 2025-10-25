"""
Django admin configuration for security app

Registers AccountSecurityState and UserSession models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import AccountSecurityState, UserSession


@admin.register(AccountSecurityState)
class AccountSecurityStateAdmin(admin.ModelAdmin):
    """Admin interface for AccountSecurityState model"""

    list_display = [
        'account',
        'lock_status',
        'concurrent_session_cap',
        'warning_count'
    ]
    list_filter = [
        'is_temp_locked',
        'warning_count'
    ]
    search_fields = ['account__name', 'last_flag_reason']

    fieldsets = (
        ('Account', {
            'fields': ('account',)
        }),
        ('Session Limits', {
            'fields': ('concurrent_session_cap',)
        }),
        ('Lock State', {
            'fields': ('is_temp_locked', 'last_flag_reason', 'warning_count')
        }),
    )

    def lock_status(self, obj):
        if obj.is_temp_locked:
            return format_html('<span style="color: red;">🔒 LOCKED</span>')
        return format_html('<span style="color: green;">✓ OK</span>')
    lock_status.short_description = 'Status'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin interface for UserSession model"""

    list_display = [
        'user',
        'session_key_short',
        'is_flagged_suspicious',
        'last_seen_at',
        'created_at',
        'session_duration'
    ]
    list_filter = [
        'is_flagged_suspicious',
        'created_at',
        'last_seen_at'
    ]
    search_fields = [
        'user__email',
        'user__username',
        'session_key'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-last_seen_at']

    readonly_fields = [
        'session_key',
        'created_at',
        'last_seen_at',
        'session_duration'
    ]

    fieldsets = (
        ('User & Session', {
            'fields': ('user', 'session_key', 'is_flagged_suspicious')
        }),
        ('Privacy-Protected Data', {
            'fields': ('ip_hash',),
            'description': 'IP addresses are hashed for GDPR compliance'
        }),
        ('Device Info', {
            'fields': ('user_agent',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_seen_at', 'session_duration')
        }),
    )

    def session_key_short(self, obj):
        return f"{obj.session_key[:8]}..."
    session_key_short.short_description = 'Session Key'

    def session_duration(self, obj):
        duration = timezone.now() - obj.created_at

        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m {seconds}s"
    session_duration.short_description = 'Duration'
