"""
Signal handlers for accounts app

Keeps User.current_plan in sync with Subscription changes.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from billing.models import Subscription


@receiver(post_save, sender=Subscription)
def sync_user_current_plan(sender, instance, **kwargs):
    """
    When Subscription.plan changes, update owner's current_plan.

    This keeps User.current_plan in sync for fast template/throttle lookups.
    """
    owner = instance.account.owner
    owner.current_plan = instance.plan.code
    owner.save(update_fields=['current_plan'])
