from django.contrib import admin
from .models import Plan, Subscription, UsageQuota


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'monthly_price', 'character_limit', 'api_rate_limit_per_hour']
    list_filter = ['name']
    search_fields = ['name']
    ordering = ['monthly_price']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'current_period_start', 'current_period_end', 'created_at']
    list_filter = ['status', 'plan', 'created_at']
    search_fields = ['user__username', 'user__email']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'plan')
        }),
        ('Subscription Details', {
            'fields': ('status', 'current_period_start', 'current_period_end')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UsageQuota)
class UsageQuotaAdmin(admin.ModelAdmin):
    list_display = ['user', 'characters_used', 'reset_date']
    list_filter = ['reset_date']
    search_fields = ['user__username', 'user__email']
    date_hierarchy = 'reset_date'
    ordering = ['-reset_date']
