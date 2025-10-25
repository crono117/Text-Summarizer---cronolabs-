from django.contrib import admin
from .models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'monthly_price_usd',
        'max_seats',
        'allow_team_members',
        'sla'
    ]
    list_filter = ['code', 'allow_team_members', 'sla']
    search_fields = ['code', 'display_name']
    ordering = ['monthly_price_usd']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'account',
        'plan',
        'is_trial',
        'is_canceled',
        'current_period_start',
        'current_period_end'
    ]
    list_filter = ['is_trial', 'is_canceled', 'plan']
    search_fields = ['account__name', 'stripe_subscription_id']
    ordering = ['-current_period_start']
    readonly_fields = ['stripe_subscription_id']

    fieldsets = (
        ('Account Information', {
            'fields': ('account', 'plan')
        }),
        ('Subscription Details', {
            'fields': ('current_period_start', 'current_period_end', 'stripe_subscription_id')
        }),
        ('Status', {
            'fields': ('is_trial', 'is_canceled')
        }),
    )
