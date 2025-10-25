"""
API decorators for authentication, quota enforcement, and rate limiting
"""

from functools import wraps
from django.http import JsonResponse
from django.utils import timezone
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta

from .models import APIKey, APIRequestLog
from billing.models import Subscription, Plan
from accounts.models import User


def require_api_key(view_func):
    """
    Decorator to require API key authentication via Bearer token

    Usage:
        @require_api_key
        def my_view(request):
            # request.user will be set to the authenticated user
            # request.api_key will contain the APIKey object
            pass
    """
    @wraps(view_func)
    @csrf_exempt
    def wrapper(request, *args, **kwargs):
        # Extract Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header:
            return JsonResponse({
                'detail': 'missing_authorization',
                'message': 'Authorization header is required. Use format: Authorization: Bearer <API_KEY>'
            }, status=401)

        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'detail': 'invalid_authorization_format',
                'message': 'Authorization must use Bearer token format: Authorization: Bearer <API_KEY>'
            }, status=401)

        # Extract API key from header
        api_key_value = auth_header.split('Bearer ', 1)[1].strip()

        if not api_key_value:
            return JsonResponse({
                'detail': 'empty_api_key',
                'message': 'API key cannot be empty'
            }, status=401)

        # Validate API key
        try:
            api_key = APIKey.objects.select_related('user').get(
                key=api_key_value,
                is_active=True
            )
        except APIKey.DoesNotExist:
            return JsonResponse({
                'detail': 'invalid_api_key',
                'message': 'Invalid or inactive API key. Check your settings at https://summasaas.com/dashboard/api-keys'
            }, status=401)

        # Update last used timestamp (async to avoid blocking)
        api_key.update_last_used()

        # Attach user and API key to request
        request.user = api_key.user
        request.api_key = api_key

        return view_func(request, *args, **kwargs)

    return wrapper


def enforce_quota_and_rate_limit(view_func):
    """
    Decorator to enforce quota and rate limits based on user's subscription plan

    Must be used AFTER @require_api_key decorator

    Usage:
        @require_api_key
        @enforce_quota_and_rate_limit
        def my_view(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        # 1. Get user's current subscription and plan
        try:
            # Get user's account (either owned or via membership)
            account = user.owned_accounts.first() or (
                user.account_memberships.first().account
                if user.account_memberships.exists()
                else None
            )

            if account:
                try:
                    subscription = account.subscription
                    plan = subscription.plan
                except Subscription.DoesNotExist:
                    # Fallback to FREE plan
                    plan = Plan.objects.filter(code='FREE').first()
                    if not plan:
                        return JsonResponse({
                            'detail': 'no_active_subscription',
                            'message': 'No active subscription found. Please subscribe at https://summasaas.com/pricing'
                        }, status=402)
            else:
                # No account, fallback to FREE plan
                plan = Plan.objects.filter(code='FREE').first()
                if not plan:
                    return JsonResponse({
                        'detail': 'no_active_subscription',
                        'message': 'No active subscription found. Please subscribe at https://summasaas.com/pricing'
                    }, status=402)
        except Exception as e:
            return JsonResponse({
                'detail': 'subscription_error',
                'message': 'Error retrieving subscription information'
            }, status=500)

        # 2. Check rate limit (requests per hour)
        current_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
        cache_key = f"rate_limit:{user.id}:{current_hour.isoformat()}"
        requests_this_hour = cache.get(cache_key, 0)

        if requests_this_hour >= plan.req_per_hour:
            return JsonResponse({
                'detail': 'rate_limit_exceeded',
                'retry_after': 3600,
                'requests_this_hour': requests_this_hour,
                'limit': plan.req_per_hour,
                'plan': plan.code,
                'message': f'Rate limit exceeded. You have {plan.req_per_hour} requests/hour on the {plan.display_name} plan. Try again in {60 - timezone.now().minute} minutes.'
            }, status=429)

        # 3. Pre-check quota (estimate character count from request body)
        try:
            text = request.data.get('text', '') if hasattr(request, 'data') else request.POST.get('text', '')
            estimated_chars = len(text)
        except Exception:
            estimated_chars = 0

        # Check monthly character usage against plan limit
        if user.monthly_char_used + estimated_chars > plan.char_limit:
            return JsonResponse({
                'detail': 'quota_exceeded',
                'quota_used': user.monthly_char_used,
                'quota_limit': plan.char_limit,
                'plan': plan.code,
                'plan_display': plan.display_name,
                'upgrade_url': 'https://summasaas.com/pricing?upgrade=true',
                'message': f'Monthly character limit reached. You have used {user.monthly_char_used}/{plan.char_limit} characters. Upgrade to a higher plan for more capacity.'
            }, status=402)

        # 4. Execute the view
        response = view_func(request, *args, **kwargs)

        # 5. Post-execution: Update usage if request was successful
        if response.status_code == 200 and estimated_chars > 0:
            # Update user's monthly character usage
            user.monthly_char_used += estimated_chars
            user.monthly_requests_used += 1
            user.save(update_fields=['monthly_char_used', 'monthly_requests_used'])

            # Increment rate limit counter
            cache.set(cache_key, requests_this_hour + 1, timeout=3600)

        return response

    return wrapper


def log_api_request(view_func):
    """
    Decorator to log API requests for analytics and monitoring

    Must be used AFTER @require_api_key decorator

    Usage:
        @require_api_key
        @log_api_request
        def my_view(request):
            pass
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        import time

        start_time = time.time()
        user = request.user
        endpoint = request.path
        method = request.method

        # Extract character count if available
        try:
            text = request.data.get('text', '') if hasattr(request, 'data') else request.POST.get('text', '')
            character_count = len(text)
        except Exception:
            character_count = 0

        # Execute the view
        response = view_func(request, *args, **kwargs)

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)

        # Log the request (async to avoid blocking)
        try:
            APIRequestLog.objects.create(
                user=user,
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                character_count=character_count,
                response_time_ms=response_time_ms,
                error_message='' if response.status_code == 200 else f"Status {response.status_code}"
            )
        except Exception as e:
            # Don't fail the request if logging fails
            pass

        return response

    return wrapper
