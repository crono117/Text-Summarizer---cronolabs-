"""
Celery configuration for the Text Summarizer project.

This module initializes the Celery application and configures it to work
with Django settings and the Redis broker.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Create the Celery application instance
app = Celery('core')

# Load task modules from all registered Django app configs.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix in Django settings.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks in all installed apps
# This will look for tasks.py files in each Django app
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery configuration."""
    print(f'Request: {self.request!r}')
