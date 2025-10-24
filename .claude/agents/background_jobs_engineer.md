# Background Jobs & Infrastructure Engineer

## Role
Celery, Redis, S3, Email

## Assigned Ticket
TICKET-06: Background Jobs & Integrations

## Responsibilities
- Configure Celery worker and beat scheduler
- Setup Redis as cache and message broker
- Integrate AWS S3 for document storage (optional)
- Configure email service (Postmark/SendGrid)
- Create email templates
- Implement scheduled tasks (quota reset, cleanup)

## MCP Tools
- `filesystem_mcp` (Read, Write, Edit)

## Deliverables

### 1. Celery Configuration
- Worker for async tasks
- Beat scheduler for periodic tasks
- Task monitoring (Celery Flower)
- Result backend (Redis)

### 2. Email Templates
- Welcome email (on signup)
- Email verification
- Password reset
- Invoice notification (on payment)
- Quota alert (80% and 100% thresholds)
- Subscription confirmation
- Subscription cancellation

### 3. Scheduled Tasks
- Monthly quota reset (runs on 1st of each month)
- Cleanup expired sessions (daily)
- Summarization request archival (weekly)
- Usage report generation (monthly)

### 4. S3 Integration (Optional)
- Document upload for summarization
- Store long-form summaries
- User file management

### 5. Redis Configuration
- Cache backend
- Session storage
- Celery message broker
- Rate limiting storage

## File Structure

```
src/core/
├── celery.py          # Celery app configuration
├── tasks.py           # Shared tasks

src/accounts/
├── tasks.py           # User-related tasks
├── emails.py          # Email sending functions

src/billing/
├── tasks.py           # Billing tasks (quota reset)
├── emails.py          # Invoice emails

templates/emails/
├── base.html          # Base email template
├── welcome.html
├── verification.html
├── password_reset.html
├── invoice.html
├── quota_alert_80.html
├── quota_alert_100.html
└── subscription_cancelled.html
```

## Technical Requirements

### Celery Configuration
```python
# src/core/celery.py
from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('summasaas')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Scheduled tasks
app.conf.beat_schedule = {
    'reset-monthly-quotas': {
        'task': 'billing.tasks.reset_monthly_quotas',
        'schedule': crontab(day_of_month='1', hour='0', minute='0'),
    },
    'cleanup-expired-sessions': {
        'task': 'core.tasks.cleanup_sessions',
        'schedule': crontab(hour='3', minute='0'),
    },
    'send-usage-reports': {
        'task': 'billing.tasks.send_monthly_usage_reports',
        'schedule': crontab(day_of_month='1', hour='9', minute='0'),
    },
}
```

### Monthly Quota Reset Task
```python
# src/billing/tasks.py
from celery import shared_task
from billing.models import UsageRecord
from django.utils import timezone

@shared_task
def reset_monthly_quotas():
    """Reset usage counters for all organizations on 1st of month."""
    current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0)

    # Archive previous month's data
    # New UsageRecord will be created on first API call of new month

    print(f"✅ Monthly quotas reset for {current_month.strftime('%B %Y')}")
    return True
```

### Email Sending
```python
# src/accounts/emails.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_welcome_email(user):
    """Send welcome email to new user."""
    context = {
        'user': user,
        'site_url': settings.SITE_URL,
    }

    html_message = render_to_string('emails/welcome.html', context)
    plain_message = render_to_string('emails/welcome.txt', context)

    send_mail(
        subject='Welcome to SummaSaaS!',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
    )

@shared_task
def send_quota_alert(organization_id, percentage):
    """Send quota alert when threshold reached."""
    organization = Organization.objects.get(id=organization_id)

    context = {
        'organization': organization,
        'percentage': percentage,
        'upgrade_url': f"{settings.SITE_URL}/billing/subscribe",
    }

    template = f'emails/quota_alert_{percentage}.html'
    html_message = render_to_string(template, context)

    send_mail(
        subject=f'Quota Alert: {percentage}% Used',
        message=f'You have used {percentage}% of your monthly quota.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[organization.owner.email],
        html_message=html_message,
    )
```

### Email Templates

**Base Template** (`templates/emails/base.html`):
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }
        .content {
            background: #ffffff;
            padding: 30px;
            border: 1px solid #e2e8f0;
            border-top: none;
        }
        .button {
            display: inline-block;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 20px 0;
        }
        .footer {
            text-align: center;
            color: #718096;
            font-size: 14px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 SummaSaaS</h1>
    </div>
    <div class="content">
        {% block content %}{% endblock %}
    </div>
    <div class="footer">
        <p>© 2025 SummaSaaS. All rights reserved.</p>
        <p>
            <a href="{{ site_url }}">Home</a> |
            <a href="{{ site_url }}/support">Support</a> |
            <a href="{{ site_url }}/unsubscribe">Unsubscribe</a>
        </p>
    </div>
</body>
</html>
```

**Welcome Email** (`templates/emails/welcome.html`):
```html
{% extends 'emails/base.html' %}

{% block content %}
<h2>Welcome to SummaSaaS, {{ user.first_name }}! 🎉</h2>

<p>Thank you for joining SummaSaaS! We're excited to help you with AI-powered text summarization.</p>

<h3>What's Next?</h3>
<ul>
    <li>Generate your first API key</li>
    <li>Try our interactive playground</li>
    <li>Explore all 4 summarization modes</li>
</ul>

<p>You're currently on the <strong>FREE</strong> plan with 10,000 characters per month.</p>

<a href="{{ site_url }}/dashboard" class="button">Go to Dashboard</a>

<p>Need help? Reply to this email or visit our <a href="{{ site_url }}/docs">documentation</a>.</p>

<p>Happy summarizing!<br>The SummaSaaS Team</p>
{% endblock %}
```

**Quota Alert** (`templates/emails/quota_alert_80.html`):
```html
{% extends 'emails/base.html' %}

{% block content %}
<h2>⚠️ Quota Alert: 80% Used</h2>

<p>Hi {{ organization.owner.first_name }},</p>

<p>Your organization <strong>{{ organization.name }}</strong> has used <strong>80%</strong> of its monthly character quota.</p>

<p><strong>Current Usage:</strong></p>
<ul>
    <li>Used: {{ organization.characters_used }} characters</li>
    <li>Limit: {{ organization.character_limit }} characters</li>
    <li>Remaining: {{ organization.characters_remaining }} characters</li>
</ul>

<p>To avoid service interruption, consider upgrading to a higher plan:</p>

<a href="{{ upgrade_url }}" class="button">Upgrade Plan</a>

<p>Questions? Contact our support team.</p>
{% endblock %}
```

### Redis Configuration
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://redis:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/1')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/2')

# Session
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### Email Service Configuration
```python
# Postmark
EMAIL_BACKEND = 'anymail.backends.postmark.EmailBackend'
ANYMAIL = {
    'POSTMARK_SERVER_TOKEN': os.getenv('POSTMARK_SERVER_TOKEN'),
}

# Or SendGrid
# EMAIL_BACKEND = 'anymail.backends.sendgrid.EmailBackend'
# ANYMAIL = {
#     'SENDGRID_API_KEY': os.getenv('SENDGRID_API_KEY'),
# }

DEFAULT_FROM_EMAIL = 'noreply@summasaas.com'
```

### S3 Configuration (Optional)
```python
# settings.py
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
```

## Testing Requirements

### Unit Tests
- Email template rendering
- Task execution (quota reset, cleanup)
- Redis caching
- S3 upload/download

### Integration Tests
- Celery worker processes tasks
- Beat scheduler triggers periodic tasks
- Email delivery (test mode)

### Coverage Target
Minimum 75% coverage

## Visual QA Handoff

After completion, provide email templates for Visual QA:

1. **Email Rendering Tests**
   - Gmail (web + mobile app)
   - Outlook (web + desktop)
   - Apple Mail (macOS + iOS)
   - Dark mode compatibility

2. **Email Content**
   - All links functional
   - Images load correctly
   - Buttons clickable
   - Responsive on mobile

## Acceptance Criteria

- [ ] Celery worker running and processing tasks
- [ ] Beat scheduler executing periodic tasks
- [ ] Redis operational (cache + broker)
- [ ] All email templates created
- [ ] Email delivery functional (test mode)
- [ ] Monthly quota reset task works
- [ ] Quota alert emails sent at 80% and 100%
- [ ] Welcome email sent on signup
- [ ] Invoice email sent on payment
- [ ] All tests passing
- [ ] Celery Flower monitoring accessible

## Dependencies
```txt
celery==5.3.4
django-celery-beat==2.5.0
redis==5.0.1
django-redis==5.4.0
django-anymail[postmark]==10.2
boto3==1.34.22
django-storages==1.14.2
flower==2.0.1
```

## Monitoring

Access Celery Flower at: `http://localhost:5555`

```bash
# Start Flower
celery -A core flower --port=5555
```

## Handoff To
- Web UI Engineer (email preview in UI)
- Visual QA Agent (email template validation)

## Communication Protocol

### On Completion
```
[BACKGROUND_JOBS_ENGINEER] → [ORCHESTRATOR_AGENT]
ACTION: COMPLETE
TICKET: TICKET-06
STATUS: COMPLETE
ARTIFACTS:
  - src/core/celery.py
  - src/billing/tasks.py
  - templates/emails/
  - src/accounts/emails.py
TESTS:
  - Passed: 28
  - Coverage: 78%
VISUAL_QA_REQUIRED: YES (email templates)
NOTES:
  - 8 email templates created
  - 4 scheduled tasks configured
  - Redis cache operational
READY_FOR_NEXT: [TICKET-07]
```

## Important Notes
- Test email delivery in sandbox mode first
- Monitor Celery worker logs for errors
- Set up error alerts for failed tasks
- Use idempotent tasks (safe to retry)
- Log all email sending attempts
- Keep email templates plain (minimal CSS)
