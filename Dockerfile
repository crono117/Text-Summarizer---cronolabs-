# Multi-stage Dockerfile for SummaSaaS

# Base stage with common dependencies
FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base as development

# Install development dependencies
RUN apt-get update && apt-get install -y \
    git \
    vim \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/base.txt requirements/dev.txt /app/requirements/
RUN pip install --upgrade pip && \
    pip install -r requirements/dev.txt

# Install Playwright browsers for visual validation
# Commented out for initial setup - install manually if needed for E2E tests
# RUN pip install playwright && \
#     playwright install --with-deps chromium firefox webkit

COPY . /app/

# Create non-root user
RUN useradd -m -u 1000 summasaas && \
    chown -R summasaas:summasaas /app
USER summasaas

EXPOSE 8000

# Production stage
FROM base as production

# Install only production dependencies
COPY requirements/base.txt requirements/prod.txt /app/requirements/
RUN pip install --upgrade pip && \
    pip install -r requirements/prod.txt

COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Create non-root user
RUN useradd -m -u 1000 summasaas && \
    chown -R summasaas:summasaas /app
USER summasaas

EXPOSE 8000

# Use gunicorn in production
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2"]
