# 🧠 SummaSaaS - AI Text Summarization SaaS Platform

> **Multi-Agent Development Project** - Built using Claude Code orchestration with visual validation pipeline

[![CI Pipeline](https://github.com/cronolabs/Text-Summarizer/actions/workflows/ci.yml/badge.svg)](https://github.com/cronolabs/Text-Summarizer/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.0](https://img.shields.io/badge/django-5.0-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Project Overview

**SummaSaaS** is a production-ready SaaS platform that provides AI-powered text summarization through a subscription-based API. Built with Django 5.0, it features:

- **4 Subscription Tiers** (FREE, STARTER, PRO, ENTERPRISE) with Stripe billing
- **4 Summarization Modes** (Extractive, Abstractive, Hybrid, Keyword Extraction)
- **Usage-Based Quotas** with real-time tracking
- **REST API** with API key authentication
- **Interactive Playground** for testing summarization
- **Visual QA Pipeline** with Playwright for automated testing

This project is developed using a **multi-agent architecture** where specialized AI agents handle different aspects of development, with automated visual validation at every quality gate.

---

## 🏗️ Architecture

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5.0 + Django REST Framework |
| **Database** | PostgreSQL 15 |
| **Cache/Queue** | Redis 7 + Celery |
| **Payment** | Stripe |
| **Storage** | AWS S3 |
| **Email** | Postmark |
| **Frontend** | Django Templates + HTMX + Tailwind CSS |
| **Testing** | Pytest + Playwright (Visual QA) |
| **CI/CD** | GitHub Actions |
| **Deployment** | Docker + Render/Railway |

### System Design

```
┌─────────────────┐
│   Web Browser   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  Django Web App │◄────►│  PostgreSQL  │
└────────┬────────┘      └──────────────┘
         │
         ├──────────┐
         │          │
         ▼          ▼
┌─────────────┐  ┌─────────────┐
│   Redis     │  │   Celery    │
│   Cache     │  │   Worker    │
└─────────────┘  └──────┬──────┘
                        │
                        ▼
              ┌──────────────────┐
              │  NLP Summarizer  │
              │  (Transformers)  │
              └──────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose** (recommended)
- **Python 3.11+** (for local development)
- **PostgreSQL 15** (if not using Docker)
- **Redis 7** (if not using Docker)
- **Stripe Account** (for billing features)

### Installation

#### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/cronolabs/Text-Summarizer.git
cd Text-Summarizer

# Copy environment template
cp .env.example .env
# Edit .env with your credentials (Stripe keys, DB passwords, etc.)

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access the application
open http://localhost:8000
```

#### Option 2: Local Development

```bash
# Clone repository
git clone https://github.com/cronolabs/Text-Summarizer.git
cd Text-Summarizer

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt

# Install Playwright browsers (for visual tests)
playwright install --with-deps

# Setup PostgreSQL and Redis (manually or via Homebrew/apt)
# Then configure DATABASE_URL and REDIS_URL in .env

# Copy environment file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

---

## 📚 Documentation Structure

- [`/docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - System architecture and design decisions
- [`/docs/API.md`](docs/API.md) - REST API documentation
- [`/docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) - Deployment guide for production
- [`/project_state/AGENT_ROSTER.md`](project_state/AGENT_ROSTER.md) - Multi-agent development roster
- [`/project_state/COMMUNICATION_PROTOCOL.md`](project_state/COMMUNICATION_PROTOCOL.md) - Inter-agent communication protocol
- [`/tests/e2e_playwright/README.md`](tests/e2e_playwright/README.md) - Visual QA testing guide

---

## 🎯 Features

### 1. Multi-Tier Subscriptions

| Plan | Monthly Price | Character Limit | API Rate Limit | Features |
|------|--------------|----------------|----------------|----------|
| **FREE** | $0 | 10,000 chars | 10 req/hour | Basic summarization |
| **STARTER** | $9.99 | 100,000 chars | 100 req/hour | All modes + email support |
| **PRO** | $29.99 | 1,000,000 chars | 1,000 req/hour | Priority processing + custom models |
| **ENTERPRISE** | $99.99 | 10,000,000 chars | Unlimited | Dedicated support + SLA |

### 2. Summarization Modes

- **Extractive (TextRank)**: Selects key sentences from original text
- **Abstractive (T5/BART)**: Generates new paraphrased summary
- **Hybrid**: Combines extractive + abstractive techniques
- **Keyword Extraction**: Identifies key terms and phrases

### 3. API Integration

```python
import requests

url = "https://api.summasaas.com/v1/summarize"
headers = {"Authorization": "Bearer YOUR_API_KEY"}
payload = {
    "text": "Your long text here...",
    "mode": "abstractive",
    "max_length": 150
}

response = requests.post(url, json=payload, headers=headers)
summary = response.json()["summary"]
```

### 4. Interactive Playground

- Test all summarization modes in real-time
- Adjust parameters (length, mode, model)
- View usage statistics
- Copy API-ready code snippets

---

## 🧪 Testing

### Backend Tests (Pytest)

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test category
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests
```

### Visual QA Tests (Playwright)

```bash
# Run all Playwright tests
pytest tests/e2e_playwright/

# Run specific viewport tests
pytest tests/e2e_playwright/ -m mobile

# Run with visual debugging (headed mode)
pytest tests/e2e_playwright/ --headed

# Run smoke tests only
pytest tests/e2e_playwright/ -m smoke
```

### Manual Testing Checklist

- [ ] User signup and email verification
- [ ] Login with credentials
- [ ] Subscription upgrade flow (Stripe checkout)
- [ ] API key generation
- [ ] Text summarization (all 4 modes)
- [ ] Usage quota tracking
- [ ] Billing portal access
- [ ] Password reset flow

---

## 📦 Deployment

### Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Stripe
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
EMAIL_HOST_USER=your_postmark_token
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# AWS S3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_STORAGE_BUCKET_NAME=your-bucket
```

### Deploy to Render

```bash
# 1. Create new Web Service on Render
# 2. Connect GitHub repository
# 3. Configure environment variables
# 4. Set build command:
pip install -r requirements/prod.txt && python manage.py collectstatic --noinput

# 5. Set start command:
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 4

# 6. Add PostgreSQL database
# 7. Add Redis instance
# 8. Deploy!
```

### Deploy to Railway

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and initialize
railway login
railway init

# 3. Add services
railway add --database postgres
railway add --database redis

# 4. Deploy
railway up

# 5. Configure environment variables via dashboard
```

---

## 🤝 Multi-Agent Development

This project is built using **Claude Code's multi-agent orchestration** with the following specialized agents:

1. **Orchestrator Agent** - Project management and coordination
2. **Visual QA Agent** - Automated visual validation with Playwright
3. **Django Core Engineer** - Authentication and core backend
4. **Billing Engineer** - Stripe integration and subscriptions
5. **Summarization Engineer** - NLP model integration
6. **API Engineer** - REST API and rate limiting
7. **Background Jobs Engineer** - Celery tasks and email
8. **Web UI Engineer** - Frontend templates and styling
9. **QA/CI Engineer** - Testing infrastructure
10. **Release Engineer** - Deployment and monitoring

See [`/project_state/AGENT_ROSTER.md`](project_state/AGENT_ROSTER.md) for detailed agent responsibilities.

---

## 🎫 Development Roadmap

| Ticket | Status | Agent | Description |
|--------|--------|-------|-------------|
| TICKET-01 | ✅ COMPLETE | Orchestrator | Infrastructure setup |
| TICKET-02 | ⏸️ PENDING | Django Core | Authentication system |
| TICKET-03 | ⏸️ PENDING | Billing | Stripe subscriptions |
| TICKET-04 | ⏸️ PENDING | Summarization | NLP engine integration |
| TICKET-05 | ⏸️ PENDING | API | REST API endpoints |
| TICKET-06 | ⏸️ PENDING | Background Jobs | Celery + Email |
| TICKET-07 | ⏸️ PENDING | Web UI | Frontend templates |
| TICKET-08 | ⏸️ PENDING | QA/CI | Testing suite |
| TICKET-09 | ⏸️ PENDING | Release | Production deployment |

---

## 🛠️ Development Commands

```bash
# Django management
python manage.py makemigrations          # Create migrations
python manage.py migrate                 # Apply migrations
python manage.py createsuperuser         # Create admin user
python manage.py shell                   # Django shell
python manage.py test                    # Run Django tests

# Celery
celery -A core worker -l info            # Start worker
celery -A core beat -l info              # Start scheduler
celery -A core flower                    # Start monitoring UI

# Code quality
black src/ tests/                        # Format code
isort src/ tests/                        # Sort imports
flake8 src/ tests/                       # Lint code
pytest --cov                             # Run tests with coverage

# Docker
docker-compose up -d                     # Start services
docker-compose down                      # Stop services
docker-compose logs -f web               # View logs
docker-compose exec web bash             # Shell into container
```

---

## 📊 Project State Tracking

Agent progress is tracked in:
- `/project_state/orchestrator_state.json` - Overall project status
- `/project_state/tickets/ticket-{N}_state.json` - Individual ticket state
- `/project_state/tickets/ticket-{N}_qa_report.json` - Visual QA validation reports
- `/project_state/agent_logs/` - Detailed agent execution logs

---

## 🐛 Troubleshooting

### Docker Issues

**Problem**: `web` service fails to start
```bash
# Check logs
docker-compose logs web

# Common fix: rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Database Issues

**Problem**: `relation does not exist` error
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Check migration status
docker-compose exec web python manage.py showmigrations
```

### Celery Issues

**Problem**: Tasks not processing
```bash
# Check worker logs
docker-compose logs worker

# Restart worker
docker-compose restart worker

# Verify Redis connection
docker-compose exec redis redis-cli ping
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- **Base Summarizer**: [venugopalkadamba/Text_Summarizer_NLP_Project](https://github.com/venugopalkadamba/Text_Summarizer_NLP_Project)
- **SaaS Framework**: [djaodjin/djaodjin-saas](https://github.com/djaodjin/djaodjin-saas)
- **Built with**: [Claude Code](https://claude.com/code) multi-agent orchestration

---

## 📧 Support

- **Documentation**: [/docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/cronolabs/Text-Summarizer/issues)
- **Email**: support@summasaas.com

---

**Built by crono117 using Claude Code Multi-Agent Orchestration** 🤖

*Last Updated: 2025-10-16*