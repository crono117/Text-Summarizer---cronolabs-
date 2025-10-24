from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Plan(models.Model):
    """Billing plans available for users"""

    PLAN_CHOICES = [
        ('FREE', 'Free'),
        ('STARTER', 'Starter'),
        ('PRO', 'Pro'),
        ('ENTERPRISE', 'Enterprise'),
    ]

    name = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        unique=True,
        help_text="Name of the billing plan"
    )
    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Monthly subscription price in USD"
    )
    character_limit = models.IntegerField(
        help_text="Maximum characters allowed per month"
    )
    api_rate_limit_per_hour = models.IntegerField(
        help_text="Maximum API requests allowed per hour"
    )
    features = models.JSONField(
        default=dict,
        help_text="Additional features included in this plan"
    )

    class Meta:
        ordering = ['monthly_price']
        verbose_name = 'Plan'
        verbose_name_plural = 'Plans'

    def __str__(self):
        return f"{self.get_name_display()} - ${self.monthly_price}/month"


class Subscription(models.Model):
    """User subscription to a billing plan"""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        help_text="User who owns this subscription"
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        help_text="Billing plan for this subscription"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Current status of the subscription"
    )
    current_period_start = models.DateTimeField(
        help_text="Start date of the current billing period"
    )
    current_period_end = models.DateTimeField(
        help_text="End date of the current billing period"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when subscription was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when subscription was last updated"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.plan.get_name_display()} ({self.status})"

    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == 'active' and self.current_period_end >= timezone.now()


class UsageQuota(models.Model):
    """Track user's usage quota for the current period"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='usage_quotas',
        help_text="User whose quota is being tracked"
    )
    characters_used = models.IntegerField(
        default=0,
        help_text="Number of characters used in the current period"
    )
    reset_date = models.DateField(
        help_text="Date when the quota will be reset"
    )

    class Meta:
        ordering = ['-reset_date']
        verbose_name = 'Usage Quota'
        verbose_name_plural = 'Usage Quotas'
        unique_together = ['user', 'reset_date']
        indexes = [
            models.Index(fields=['user', 'reset_date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.characters_used} chars used (resets: {self.reset_date})"

    def remaining_characters(self, plan):
        """Calculate remaining characters for a given plan"""
        return max(0, plan.character_limit - self.characters_used)

    def can_process(self, character_count, plan):
        """Check if user can process given number of characters"""
        return self.characters_used + character_count <= plan.character_limit
