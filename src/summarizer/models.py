from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SummarizationTask(models.Model):
    """Represents a summarization task submitted by a user"""

    MODE_CHOICES = [
        ('extractive', 'Extractive'),
        ('abstractive', 'Abstractive'),
        ('hybrid', 'Hybrid'),
        ('keyword', 'Keyword'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='summarization_tasks',
        help_text="User who submitted the task"
    )
    input_text = models.TextField(
        help_text="Original text to be summarized"
    )
    mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        help_text="Summarization mode to use"
    )
    max_length = models.IntegerField(
        default=150,
        help_text="Maximum length of the summary in words"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the task"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when task was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when task was last updated"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Summarization Task'
        verbose_name_plural = 'Summarization Tasks'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Task {self.id} - {self.user.username} ({self.get_mode_display()}) - {self.status}"

    def get_input_preview(self, length=50):
        """Return a preview of the input text"""
        if len(self.input_text) <= length:
            return self.input_text
        return f"{self.input_text[:length]}..."

    def mark_completed(self):
        """Mark the task as completed"""
        self.status = 'completed'
        self.save(update_fields=['status', 'updated_at'])

    def mark_failed(self):
        """Mark the task as failed"""
        self.status = 'failed'
        self.save(update_fields=['status', 'updated_at'])


class SummaryResult(models.Model):
    """Stores the result of a completed summarization task"""

    task = models.OneToOneField(
        SummarizationTask,
        on_delete=models.CASCADE,
        related_name='result',
        help_text="Associated summarization task"
    )
    output_text = models.TextField(
        help_text="Generated summary text"
    )
    characters_processed = models.IntegerField(
        help_text="Number of characters processed from input"
    )
    processing_time_ms = models.IntegerField(
        help_text="Time taken to process in milliseconds"
    )

    class Meta:
        verbose_name = 'Summary Result'
        verbose_name_plural = 'Summary Results'
        indexes = [
            models.Index(fields=['task']),
        ]

    def __str__(self):
        return f"Result for Task {self.task.id} - {self.characters_processed} chars in {self.processing_time_ms}ms"

    def get_output_preview(self, length=50):
        """Return a preview of the output text"""
        if len(self.output_text) <= length:
            return self.output_text
        return f"{self.output_text[:length]}..."

    def get_compression_ratio(self):
        """Calculate the compression ratio of the summary"""
        if self.characters_processed == 0:
            return 0
        return (len(self.output_text) / self.characters_processed) * 100
