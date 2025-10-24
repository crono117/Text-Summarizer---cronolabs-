# Quick Start Guide - SummaSaaS

## Test Credentials

**Username**: testuser
**Email**: test@example.com
**Password**: testpass123
**Plan**: Free (active)

## Access the Application

- **Home**: http://localhost:8000/
- **Pricing**: http://localhost:8000/billing/pricing/
- **Login**: http://localhost:8000/accounts/login/
- **Signup**: http://localhost:8000/accounts/signup/
- **Dashboard**: http://localhost:8000/dashboard/ (requires login)
- **Admin**: http://localhost:8000/admin/ (requires superuser)

## Useful Commands

### Seed Database with Plans
```bash
docker-compose -f docker-compose.lite.yml exec web python manage.py seed_plans
```

### Run Application Tests
```bash
docker-compose -f docker-compose.lite.yml exec web python test_application.py
```

### Create Superuser (for Django Admin)
```bash
docker-compose -f docker-compose.lite.yml exec web python manage.py createsuperuser
```

### Django Shell
```bash
docker-compose -f docker-compose.lite.yml exec web python manage.py shell
```

### View Logs
```bash
# Web server logs
docker-compose -f docker-compose.lite.yml logs -f web

# All services logs
docker-compose -f docker-compose.lite.yml logs -f
```

### Check Database
```bash
# PostgreSQL shell
docker-compose -f docker-compose.lite.yml exec db psql -U postgres -d summasaas

# List all plans in database
docker-compose -f docker-compose.lite.yml exec web python manage.py shell -c "from billing.models import Plan; [print(p) for p in Plan.objects.all()]"
```

## Subscription Plans

| Plan | Price | Characters/Month | Requests/Hour | Key Features |
|------|-------|------------------|---------------|--------------|
| FREE | $0 | 10,000 | 10 | Basic summarization |
| STARTER | $9.99 | 100,000 | 100 | + API access, Save summaries |
| PRO | $29.99 | 1,000,000 | 1,000 | + Batch processing, Priority support |
| ENTERPRISE | $99.99 | 10,000,000 | Unlimited | + Custom models, SLA, Dedicated support |

## Application Status

All systems operational:
- ✅ Web server running on port 8000
- ✅ PostgreSQL database ready
- ✅ Redis cache ready
- ✅ Celery worker running
- ✅ All 4 subscription plans loaded
- ✅ Test user created with active subscription

## Next Steps

1. **Login**: Use test credentials to access dashboard
2. **View Pricing**: Check out the pricing page to see all plans
3. **Create Content**: Try the summarization features
4. **Admin Panel**: Create a superuser to access Django admin
5. **Development**: Start building new features!

For detailed information, see `DATA_SEEDING_REPORT.md`
