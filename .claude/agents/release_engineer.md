# Release Engineer

## Role
Deployment & Launch

## Assigned Ticket
TICKET-09: Deployment & Launch

## Responsibilities
- Setup production environment (Render/Railway)
- Configure environment variables and secrets
- Run database migrations in production
- Setup static files serving (CDN)
- Configure domain and SSL certificates
- Implement health check endpoint
- Setup error monitoring (Sentry)
- Execute production smoke tests
- Create rollback plan

## MCP Tools
- `github_mcp` (via gh CLI)
- `filesystem_mcp` (Read, Write, Edit)
- `playwright_mcp` (for production smoke tests)

## Deliverables

### 1. Production Environment

**Platform**: Render or Railway (choose one)

#### Services to Deploy
- **Web Service** (Django app with Gunicorn)
- **Worker Service** (Celery worker)
- **Beat Service** (Celery beat scheduler)
- **PostgreSQL** (managed database)
- **Redis** (managed cache/broker)

### 2. Environment Configuration

All production secrets configured:
- Django SECRET_KEY (generated, secure)
- DATABASE_URL (production PostgreSQL)
- REDIS_URL (production Redis)
- Stripe keys (production mode)
- Email service credentials
- AWS S3 credentials
- Sentry DSN
- Allowed hosts

### 3. Database Migration

- Run all migrations safely
- Create database backup before migration
- Test migrations on staging first
- Document migration process

### 4. Static Files & CDN

- Collect static files
- Upload to S3 or CDN
- Configure WhiteNoise (fallback)
- Verify all assets load

### 5. Domain & SSL

- Configure custom domain
- Setup SSL certificate (Let's Encrypt)
- Force HTTPS redirect
- Configure security headers

### 6. Monitoring & Error Tracking

- Sentry integration
- Health check endpoint
- Uptime monitoring
- Performance monitoring (optional)

### 7. Smoke Tests

Run production smoke tests with Playwright

## File Structure

```
deployment/
├── render.yaml            # Render configuration
├── railway.json           # Railway configuration (alternative)
├── health_check.py        # Health check endpoint
├── smoke_tests.py         # Production validation
└── rollback.md            # Rollback procedure

scripts/
├── deploy.sh              # Deployment script
├── migrate.sh             # Migration script
└── seed_data.py           # Optional seed data
```

## Technical Requirements

### Render Configuration
```yaml
# render.yaml
services:
  # Web Service
  - type: web
    name: summasaas-web
    env: python
    region: oregon
    plan: starter
    buildCommand: pip install -r requirements/prod.txt && python manage.py collectstatic --noinput
    startCommand: gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: DEBUG
        value: False
      - key: SECRET_KEY
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: summasaas-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: summasaas-redis
          type: redis
          property: connectionString

  # Celery Worker
  - type: worker
    name: summasaas-worker
    env: python
    buildCommand: pip install -r requirements/prod.txt
    startCommand: celery -A core worker -l info
    envVars:
      # Same as web service

  # Celery Beat
  - type: worker
    name: summasaas-beat
    env: python
    buildCommand: pip install -r requirements/prod.txt
    startCommand: celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    envVars:
      # Same as web service

databases:
  - name: summasaas-db
    plan: starter
    databaseName: summasaas
    user: summasaas

  - name: summasaas-redis
    plan: starter
```

### Health Check Endpoint
```python
# src/core/health.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis

def health_check(request):
    """Health check endpoint for monitoring."""
    status = {
        'status': 'healthy',
        'checks': {}
    }

    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        status['checks']['database'] = 'ok'
    except Exception as e:
        status['checks']['database'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'

    # Redis check
    try:
        cache.set('health_check', 'ok', 10)
        assert cache.get('health_check') == 'ok'
        status['checks']['redis'] = 'ok'
    except Exception as e:
        status['checks']['redis'] = f'error: {str(e)}'
        status['status'] = 'unhealthy'

    # Celery check (optional)
    try:
        from celery import current_app
        inspect = current_app.control.inspect()
        stats = inspect.stats()
        status['checks']['celery'] = 'ok' if stats else 'no workers'
    except Exception as e:
        status['checks']['celery'] = f'error: {str(e)}'

    return JsonResponse(status, status=200 if status['status'] == 'healthy' else 503)

# Add to urls.py
path('health/', health_check, name='health'),
```

### Production Settings
```python
# settings.py (production section)
if not DEBUG:
    # Security
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

    # Allowed hosts
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

    # Static files (S3 or WhiteNoise)
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    # Logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }

    # Sentry
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )
```

### Deployment Script
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

echo "🚀 Starting deployment..."

# 1. Verify environment
echo "1️⃣ Verifying environment variables..."
required_vars=("DATABASE_URL" "REDIS_URL" "SECRET_KEY" "STRIPE_SECRET_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required variable: $var"
        exit 1
    fi
done

# 2. Install dependencies
echo "2️⃣ Installing dependencies..."
pip install -r requirements/prod.txt

# 3. Collect static files
echo "3️⃣ Collecting static files..."
python manage.py collectstatic --noinput

# 4. Run migrations
echo "4️⃣ Running database migrations..."
python manage.py migrate --noinput

# 5. Check deployment
echo "5️⃣ Running Django checks..."
python manage.py check --deploy

# 6. Start services
echo "6️⃣ Starting Gunicorn..."
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2

echo "✅ Deployment complete!"
```

### Production Smoke Tests
```python
# tests/e2e_playwright/test_production_smoke.py
import pytest
from playwright.sync_api import Page, expect
import os

PRODUCTION_URL = os.getenv('PRODUCTION_URL', 'https://summasaas.com')

@pytest.mark.production
def test_homepage_loads(page: Page):
    """Test production homepage loads."""
    page.goto(PRODUCTION_URL)

    # Verify page loads
    expect(page).to_have_title(re.compile('SummaSaaS'))

    # Verify SSL
    assert page.url.startswith('https://')

    # Screenshot
    page.screenshot(path='artifacts/production-homepage.png')

@pytest.mark.production
def test_health_check_endpoint(page: Page):
    """Test health check endpoint."""
    response = page.request.get(f'{PRODUCTION_URL}/health/')

    assert response.status == 200

    body = response.json()
    assert body['status'] == 'healthy'
    assert body['checks']['database'] == 'ok'
    assert body['checks']['redis'] == 'ok'

@pytest.mark.production
def test_critical_user_path(page: Page):
    """Test signup → subscribe → summarize flow in production."""

    # 1. Visit homepage
    page.goto(PRODUCTION_URL)
    expect(page.locator('h1')).to_be_visible()

    # 2. Navigate to signup
    page.click('a:has-text("Sign Up")')
    expect(page).to_have_url(re.compile('/signup'))

    # 3. Verify signup form present
    expect(page.locator('input[name="email"]')).to_be_visible()

    # 4. Navigate to pricing
    page.goto(f'{PRODUCTION_URL}/pricing')

    # 5. Verify all plans visible
    plans = page.locator('.plan-card')
    expect(plans).to_have_count(4)

    # 6. Verify API docs accessible
    page.goto(f'{PRODUCTION_URL}/api/v1/docs/')
    expect(page.locator('h1')).to_contain_text('API')

    # Critical paths accessible ✅
    page.screenshot(path='artifacts/production-smoke-test.png')

@pytest.mark.production
def test_static_files_load(page: Page):
    """Test all static assets load correctly."""
    page.goto(PRODUCTION_URL)

    # Check CSS loaded
    styles = page.locator('link[rel="stylesheet"]')
    expect(styles.first).to_have_attribute('href', re.compile('css'))

    # Check JS loaded
    scripts = page.locator('script[src]')
    expect(scripts.first).to_have_attribute('src', re.compile('js'))

    # Verify no 404s in console
    errors = []
    page.on('pageerror', lambda err: errors.append(err))
    page.reload()

    assert len(errors) == 0, f"Console errors: {errors}"
```

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing in CI
- [ ] Visual QA approved
- [ ] Database backup created
- [ ] Environment variables configured
- [ ] Secrets securely stored
- [ ] Domain DNS configured
- [ ] SSL certificate ready

### Deployment Steps
1. [ ] Deploy to staging environment
2. [ ] Run smoke tests on staging
3. [ ] Run database migrations on production
4. [ ] Deploy web service
5. [ ] Deploy worker services
6. [ ] Verify health check endpoint
7. [ ] Run production smoke tests
8. [ ] Monitor error logs (Sentry)
9. [ ] Verify Stripe webhooks working
10. [ ] Test email delivery

### Post-Deployment
- [ ] Monitor error rates (first 24 hours)
- [ ] Check performance metrics
- [ ] Verify scheduled tasks running (Celery beat)
- [ ] Test critical user flows manually
- [ ] Update documentation
- [ ] Announce launch 🎉

## Rollback Plan

If deployment fails:

```bash
# 1. Revert to previous Docker image
render rollback summasaas-web

# 2. Revert database migrations (if needed)
python manage.py migrate <app_name> <previous_migration>

# 3. Clear cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# 4. Restart services
render restart summasaas-web
render restart summasaas-worker

# 5. Verify health check
curl https://summasaas.com/health/
```

## Visual QA Handoff

After deployment, Visual QA Agent validates:

1. **Production Smoke Tests**
   - All critical paths work on live site
   - SSL valid
   - Static assets load
   - Forms submit correctly

2. **Performance Validation**
   - Page load <3 seconds
   - Lighthouse score >90
   - No console errors

## Acceptance Criteria

- [ ] Production environment deployed
- [ ] All services running (web, worker, beat, db, redis)
- [ ] Database migrated successfully
- [ ] Static files served correctly
- [ ] SSL certificate active (HTTPS enforced)
- [ ] Custom domain configured
- [ ] Health check endpoint responding
- [ ] Sentry error tracking operational
- [ ] Production smoke tests passing
- [ ] No critical errors in logs
- [ ] Visual QA approved

## Dependencies
```txt
gunicorn==21.2.0
whitenoise==6.6.0
sentry-sdk==1.40.0
```

## Monitoring

### Uptime Monitoring
- Setup UptimeRobot or similar
- Monitor `/health/` endpoint
- Alert on downtime

### Error Tracking
- Sentry dashboard: https://sentry.io
- Alert on error rate >1%
- Monitor performance issues

## Handoff To
- Orchestrator Agent (for final sign-off)
- Visual QA Agent (for production validation)

## Communication Protocol

### On Completion
```
[RELEASE_ENGINEER] → [ORCHESTRATOR_AGENT]
ACTION: COMPLETE
TICKET: TICKET-09
STATUS: COMPLETE
DEPLOYMENT:
  - Environment: Production (Render)
  - URL: https://summasaas.com
  - Services: web, worker, beat, db, redis (ALL RUNNING)
  - SSL: Active ✅
  - Health Check: https://summasaas.com/health/ (200 OK)
SMOKE_TESTS:
  - Homepage: PASS ✅
  - Signup: PASS ✅
  - Pricing: PASS ✅
  - API Docs: PASS ✅
  - Health Check: PASS ✅
VISUAL_QA_REQUIRED: YES
MONITORING:
  - Sentry: Configured ✅
  - Uptime: Monitored ✅
NOTES:
  - Zero errors in first hour
  - Performance metrics within SLA
  - Rollback plan documented
READY_FOR_LAUNCH: YES 🚀
```

## Important Notes
- Never deploy directly to production (use staging first)
- Always backup database before migrations
- Monitor error rates closely after deployment
- Have rollback plan ready
- Document all configuration changes
- Use feature flags for risky features
- Perform deployments during low-traffic periods
