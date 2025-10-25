"""
Security models for fraud prevention and account sharing detection

This module implements:
- AccountSecurityState: Tracks security events and temporary account locks
- UserSession: Tracks active sessions for concurrent session limiting
"""

from django.db import models


class AccountSecurityState(models.Model):
    """
    Fraud/abuse tracking per account.

    Support staff can manually lock/unlock accounts.
    """

    account = models.OneToOneField(
        'accounts.CustomerAccount',
        on_delete=models.CASCADE,
        related_name='security_state'
    )

    # REQUIRED: Per-account session cap override
    concurrent_session_cap = models.IntegerField(
        default=2,
        help_text="Account-specific session limit (overrides Plan default)"
    )

    # Lock state
    is_temp_locked = models.BooleanField(
        default=False,
        help_text="If True, block all API requests for this account"
    )
    last_flag_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Why account was flagged/locked"
    )
    warning_count = models.IntegerField(
        default=0,
        help_text="Number of times account has been flagged"
    )

    def __str__(self):
        status = "LOCKED" if self.is_temp_locked else "OK"
        return f"{self.account.name} - {status}"


class UserSession(models.Model):
    """
    Track active sessions for concurrency enforcement.

    IMPORTANT: Store ip_hash, not raw IP (GDPR/privacy).
    """

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='sessions'
    )

    session_key = models.CharField(
        max_length=100,
        unique=True
    )

    # CRITICAL: Hash IP, don't store raw! (spec says ip_hash, not ip_address)
    ip_hash = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="SHA256 hash of IP address for privacy"
    )

    user_agent = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)

    is_flagged_suspicious = models.BooleanField(
        default=False,
        help_text="Flagged by concurrency enforcement"
    )

    def __str__(self):
        return f"{self.user.email} - {self.session_key[:8]}..."

    @staticmethod
    def hash_ip(ip_address: str) -> str:
        """Hash IP address for privacy"""
        import hashlib
        return hashlib.sha256(ip_address.encode()).hexdigest()
