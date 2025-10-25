from django.db import models
from django.conf import settings
from django.utils import timezone


class Plan(models.Model):
    """
    Billing plan tiers.

    CRITICAL: Must have separate 'code' and 'display_name' fields.
    """

    # Identification (spec requires BOTH fields)
    code = models.CharField(
        max_length=20,
        unique=True,
        choices=[
            ('FREE', 'FREE'),
            ('PLUS', 'PLUS'),
            ('PRO', 'PRO'),
            ('ENTERPRISE', 'ENTERPRISE')
        ],
        help_text="Internal plan code (FREE, PLUS, PRO, ENTERPRISE)"
    )
    display_name = models.CharField(
        max_length=100,
        help_text="Marketing label (e.g., 'Professional Plan')"
    )

    # Pricing
    monthly_price_usd = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price in USD per month"
    )
    stripe_price_id = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Stripe Price ID (e.g., price_xxxxx)"
    )

    # Quota limits (EXACT field names from spec!)
    char_limit = models.BigIntegerField(
        help_text="Monthly character limit"
    )
    req_per_hour = models.IntegerField(
        help_text="API requests allowed per hour"
    )

    # Team features
    max_seats = models.IntegerField(
        help_text="Maximum team members (1 for FREE/PLUS, 5+ for PRO/ENTERPRISE)"
    )
    max_concurrent_sessions = models.IntegerField(
        default=2,
        help_text="Max concurrent sessions per user"
    )
    allow_team_members = models.BooleanField(
        default=False,
        help_text="Whether plan allows inviting team members"
    )

    # Support SLA
    priority_support = models.BooleanField(
        default=False,
        help_text="Dedicated support channel"
    )
    sla = models.BooleanField(
        default=False,
        help_text="SLA guarantee (99.9% uptime, etc.)"
    )

    class Meta:
        ordering = ['monthly_price_usd']

    def __str__(self):
        return f"{self.code} - ${self.monthly_price_usd}/mo"


class Subscription(models.Model):
    """
    Links CustomerAccount to a Plan.

    CRITICAL: Must be OneToOneField, not ForeignKey!
    Each account has exactly ONE active subscription at a time.
    """

    # OneToOne relationship (only 1 active subscription per account)
    account = models.OneToOneField(
        'accounts.CustomerAccount',
        on_delete=models.CASCADE,
        related_name='subscription'  # Note: singular, not plural!
    )

    plan = models.ForeignKey(
        'Plan',
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )

    # Stripe integration
    stripe_subscription_id = models.CharField(
        max_length=100,
        blank=True,
        default=''
    )

    # Billing period
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()

    # Trial state (BooleanField as spec requires, NOT status CharField!)
    is_trial = models.BooleanField(
        default=False,
        help_text="True if in trial period"
    )

    # Cancellation state (BooleanField as spec requires)
    is_canceled = models.BooleanField(
        default=False,
        help_text="True if subscription is canceled"
    )

    def __str__(self):
        return f"{self.account.name} - {self.plan.code}"

    def is_active(self) -> bool:
        """
        Subscription is active if:
        - Not canceled
        - Period hasn't expired
        - Account is active
        """
        from django.utils import timezone
        return (
            not self.is_canceled and
            self.current_period_end >= timezone.now() and
            self.account.is_active
        )
