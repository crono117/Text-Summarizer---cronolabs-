"""
Core package initialization.

This ensures that the Celery app is loaded when Django starts,
so that shared_task decorators will use this app.
"""

# Import the Celery app so it's always imported when Django starts
from .celery import app as celery_app

__all__ = ('celery_app',)
