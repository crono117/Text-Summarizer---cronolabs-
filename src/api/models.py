from django.db import models
from django.conf import settings
from django.utils import timezone
import secrets


def generate_api_key():
    """Generate a secure random API key"""
    return secrets.token_urlsafe(48)


class APIKey(models.Model):
    """API key for external access to the summarization service"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_keys',
        help_text="User who owns this API key"
    )
    key = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        default=generate_api_key,
        help_text="The API key value"
    )
    name = models.CharField(
        max_length=100,
        help_text="Descriptive name for this key (e.g., 'WordPress Plugin')"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this key is currently active"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when key was created"
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when key was last used"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.name} ({'active' if self.is_active else 'inactive'})"

    def update_last_used(self):
        """Update the last_used_at timestamp"""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])


class APIRequestLog(models.Model):
    """Log of all API requests for analytics and monitoring"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_logs',
        help_text="User who made the request"
    )
    endpoint = models.CharField(
        max_length=100,
        help_text="API endpoint that was called (e.g., '/api/v1/summarize/')"
    )
    method = models.CharField(
        max_length=10,
        help_text="HTTP method (POST, GET, etc.)"
    )
    status_code = models.IntegerField(
        help_text="HTTP response status code"
    )
    character_count = models.IntegerField(
        default=0,
        help_text="Number of characters processed in this request"
    )
    response_time_ms = models.IntegerField(
        help_text="Response time in milliseconds"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when request was made"
    )
    error_message = models.TextField(
        blank=True,
        default='',
        help_text="Error message if request failed"
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'API Request Log'
        verbose_name_plural = 'API Request Logs'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['endpoint', 'timestamp']),
            models.Index(fields=['status_code', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.method} {self.endpoint} - {self.status_code} ({self.timestamp})"
