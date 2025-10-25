"""
Multi-tenant account and authentication models

This module implements a sophisticated multi-tenant SaaS architecture:
- Custom User model with staff flags and usage tracking
- CustomerAccount for workspace/organization concept
- AccountMembership for role-based access control (RBAC)
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser

    Adds:
    - Staff permission flags (support staff, superadmin)
    - Current plan reference for quick lookups
    - Monthly usage counters for optimization
    """

    # Staff permission flags
    is_staff_support = models.BooleanField(
        default=False,
        help_text="Support staff can manage customer accounts"
    )
    is_superadmin = models.BooleanField(
        default=False,
        help_text="Superadmins have full system access"
    )

    # Denormalized plan cache (CharField, NOT ForeignKey!)
    current_plan = models.CharField(
        max_length=20,
        choices=[
            ('FREE', 'Free'),
            ('PLUS', 'Plus'),
            ('PRO', 'Pro'),
            ('ENTERPRISE', 'Enterprise')
        ],
        default='FREE',
        help_text="Cached from active Subscription.plan.code for fast lookups"
    )

    # Usage counters (BigIntegerField as spec requires)
    monthly_char_used = models.BigIntegerField(
        default=0,
        help_text="Characters processed this billing period"
    )
    monthly_requests_used = models.BigIntegerField(
        default=0,
        help_text="API requests this billing period"
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email or self.username

    # REQUIRED METHODS (spec says these must exist)
    def is_paying_customer(self) -> bool:
        """Return True if user is on a paid plan (not FREE)"""
        return self.current_plan != 'FREE'

    def is_internal(self) -> bool:
        """Return True if user is staff support or superadmin"""
        return self.is_staff_support or self.is_superadmin


class CustomerAccount(models.Model):
    """
    Workspace/organization for paying customers.

    Even solo users get a CustomerAccount.
    """

    name = models.CharField(
        max_length=200,
        help_text="Account/organization name"
    )

    # REQUIRED: Direct owner FK (spec explicitly requires this)
    owner = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        related_name='owned_accounts',
        help_text="Primary account owner"
    )

    # Stripe linkage
    stripe_customer_id = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Stripe Customer ID (cus_xxxxx)"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="False = suspended/locked"
    )

    def __str__(self):
        return self.name


class AccountMembership(models.Model):
    """
    Links users to accounts with roles (RBAC).

    Permissions:
    - OWNER: Full control (billing, members, API usage)
    - ADMIN: Manage members, no billing access
    - MEMBER: Use API only
    - READONLY: View dashboards only
    """

    ROLE_CHOICES = [
        ('OWNER', 'Owner'),
        ('ADMIN', 'Administrator'),
        ('MEMBER', 'Member'),
        ('READONLY', 'Read-Only')
    ]

    account = models.ForeignKey(
        'CustomerAccount',
        on_delete=models.CASCADE,
        related_name='memberships'
    )

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='account_memberships'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='MEMBER'
    )

    class Meta:
        unique_together = [('account', 'user')]

    def __str__(self):
        return f"{self.user.email} → {self.account.name} ({self.role})"

    def clean(self):
        """
        Enforce seat limits from Plan.max_seats.

        Raise ValidationError if adding this member would exceed limit.
        """
        super().clean()

        plan = self.account.subscription.plan
        active_members = AccountMembership.objects.filter(
            account=self.account
        ).exclude(pk=self.pk).count()

        if active_members >= plan.max_seats:
            raise ValidationError(
                f"Account has reached max seats ({plan.max_seats}). "
                f"Upgrade to add more members."
            )
