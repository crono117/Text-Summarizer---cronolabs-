"""
Core views for the SummaSaaS application.
"""

from django.http import JsonResponse
from django.shortcuts import render
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Health check endpoint that verifies database and Redis connectivity.

    Returns:
        JsonResponse: Status of the application and its dependencies
    """
    health_status = {
        "status": "ok",
        "database": "disconnected",
        "redis": "disconnected"
    }

    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["status"] = "degraded"
        health_status["database"] = "disconnected"

    # Check Redis connectivity
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status["redis"] = "connected"
        else:
            raise Exception("Redis read verification failed")
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        health_status["status"] = "degraded"
        health_status["redis"] = "disconnected"

    # Return 200 if all services are connected, 503 if degraded
    status_code = 200 if health_status["status"] == "ok" else 503

    return JsonResponse(health_status, status=status_code)


def home(request):
    """
    Home page view displaying the landing page with hero section,
    features, and call-to-action.

    Returns:
        HttpResponse: Rendered home page template
    """
    return render(request, 'home.html')
