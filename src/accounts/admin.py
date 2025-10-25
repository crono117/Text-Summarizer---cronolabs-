"""
Django admin configuration for accounts app

Registers User, CustomerAccount, and AccountMembership models with comprehensive admin interfaces.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, CustomerAccount, AccountMembership


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for custom User model"""

    list_display = [
        'email',
        'username',
        'current_plan',
        'is_staff_support',
        'is_superadmin',
        'last_login'
    ]
    list_filter = [
        'is_active',
        'is_staff',
        'is_staff_support',
        'is_superadmin',
        'current_plan',
        'date_joined'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Staff Permissions', {
            'fields': ('is_staff_support', 'is_superadmin')
        }),
        ('Plan & Usage', {
            'fields': ('current_plan', 'monthly_char_used', 'monthly_requests_used')
        }),
    )

    readonly_fields = ['last_login', 'date_joined']


@admin.register(CustomerAccount)
class CustomerAccountAdmin(admin.ModelAdmin):
    """Admin interface for CustomerAccount model"""

    list_display = ['name', 'owner', 'stripe_customer_id', 'is_active']
    search_fields = ['name', 'owner__email', 'stripe_customer_id']
    list_filter = ['is_active']

    fieldsets = (
        ('Account Information', {
            'fields': ('name', 'owner')
        }),
        ('Stripe Integration', {
            'fields': ('stripe_customer_id',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(AccountMembership)
class AccountMembershipAdmin(admin.ModelAdmin):
    """Admin interface for AccountMembership model"""

    list_display = ['user', 'account', 'role']
    search_fields = ['user__email', 'account__name']
    list_filter = ['role']

    fieldsets = (
        ('Membership', {
            'fields': ('account', 'user', 'role')
        }),
    )
