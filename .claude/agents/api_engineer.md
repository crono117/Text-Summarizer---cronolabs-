# API & Quotas Engineer

## Role
REST API & Rate Limiting

## Assigned Ticket
TICKET-05: REST API & Quotas

## Responsibilities
- Build Django REST Framework API
- Implement API key authentication
- Configure rate limiting per subscription tier
- Enforce quota limits (character usage)
- Track usage and return appropriate error codes
- Generate API documentation

## MCP Tools
- `filesystem_mcp` (Read, Write, Edit)

## Deliverables

### 1. API Endpoints

```
POST   /api/v1/summarize       # Main summarization endpoint
GET    /api/v1/usage            # Current month usage
GET    /api/v1/history          # Summarization history
GET    /api/v1/keys             # List API keys
POST   /api/v1/keys             # Create new API key
DELETE /api/v1/keys/{id}        # Revoke API key
GET    /api/v1/docs             # Swagger UI documentation
```

### 2. Authentication
- API key authentication (custom DRF auth class)
- Header format: `Authorization: Bearer {api_key}`
- Key validation and organization lookup

### 3. Rate Limiting
Per subscription tier:
- FREE: 10 requests/hour
- STARTER: 100 requests/hour
- PRO: 1,000 requests/hour
- ENTERPRISE: Unlimited

### 4. Quota Enforcement
- Check character limit before processing
- Return 402 Payment Required if quota exceeded
- Return 429 Too Many Requests if rate limit hit
- Include usage info in response headers

### 5. Usage Tracking
- Track characters used per request
- Increment organization usage counter
- Store request metadata (timestamp, mode, chars)

## File Structure

```
src/api/
├── views.py           # API viewsets
├── serializers.py     # Request/response serializers
├── authentication.py  # API key auth
├── permissions.py     # Organization permissions
├── throttling.py      # Rate limiting
├── middleware.py      # Usage tracking middleware
├── urls.py            # API routing
└── tests/
    ├── test_summarize.py
    ├── test_auth.py
    ├── test_throttling.py
    └── test_quotas.py
```

## Technical Requirements

### API Key Authentication
```python
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import APIKey

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None

        api_key_value = auth_header.replace('Bearer ', '')

        try:
            api_key = APIKey.objects.select_related('organization').get(
                key=api_key_value,
                is_active=True
            )
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')

        # Update last used
        api_key.last_used_at = timezone.now()
        api_key.save(update_fields=['last_used_at'])

        return (api_key.organization, api_key)
```

### Summarization Endpoint
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from billing.entitlements import check_quota

class SummarizeView(APIView):
    authentication_classes = [APIKeyAuthentication]

    def post(self, request):
        # Get organization from auth
        organization = request.user

        # Validate input
        text = request.data.get('text')
        mode = request.data.get('mode', 'extractive')
        max_length = request.data.get('max_length', 150)

        if not text:
            return Response(
                {'error': 'Text is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check quota
        has_quota, status_code = check_quota(organization, len(text))
        if not has_quota:
            return Response(
                {
                    'error': 'Quota exceeded',
                    'message': 'Upgrade your plan to continue',
                    'usage': get_usage_stats(organization)
                },
                status=status_code
            )

        # Perform summarization
        try:
            if mode == 'extractive':
                summary = extractive_model.summarize(text)
            elif mode == 'abstractive':
                summary = abstractive_model.summarize(text, max_length)
            elif mode == 'hybrid':
                summary = hybrid_model.summarize(text, max_length)
            elif mode == 'keywords':
                summary = keyword_model.extract_keywords(text)
            else:
                return Response(
                    {'error': 'Invalid mode'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': f'Summarization failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Track usage
        track_usage(organization, len(text), mode)

        # Return response
        return Response({
            'summary': summary,
            'mode': mode,
            'characters_used': len(text),
            'usage': get_usage_stats(organization)
        })
```

### Rate Limiting
```python
from rest_framework.throttling import UserRateThrottle

class TierBasedThrottle(UserRateThrottle):
    def get_rate(self):
        organization = self.request.user
        tier = organization.subscription_tier

        rates = {
            'FREE': '10/hour',
            'STARTER': '100/hour',
            'PRO': '1000/hour',
            'ENTERPRISE': '100000/hour',  # Effectively unlimited
        }

        return rates.get(tier, '10/hour')
```

### Serializers
```python
from rest_framework import serializers

class SummarizeRequestSerializer(serializers.Serializer):
    text = serializers.CharField(
        required=True,
        min_length=100,
        max_length=50000
    )
    mode = serializers.ChoiceField(
        choices=['extractive', 'abstractive', 'hybrid', 'keywords'],
        default='extractive'
    )
    max_length = serializers.IntegerField(
        min_value=50,
        max_value=500,
        default=150
    )

class SummarizeResponseSerializer(serializers.Serializer):
    summary = serializers.CharField()
    mode = serializers.CharField()
    characters_used = serializers.IntegerField()
    usage = serializers.DictField()

class UsageSerializer(serializers.Serializer):
    month = serializers.DateField()
    characters_used = serializers.IntegerField()
    character_limit = serializers.IntegerField()
    percentage_used = serializers.FloatField()
    api_calls_made = serializers.IntegerField()
```

### Usage Tracking
```python
from billing.models import UsageRecord
from django.utils import timezone

def track_usage(organization, characters_used, mode):
    """Increment usage for current month."""
    current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0)

    usage, created = UsageRecord.objects.get_or_create(
        organization=organization,
        month=current_month
    )

    usage.characters_used += characters_used
    usage.api_calls_made += 1
    usage.save()

    # Store individual request
    SummarizationRequest.objects.create(
        organization=organization,
        mode=mode,
        characters=characters_used,
        timestamp=timezone.now()
    )
```

## API Documentation

Use drf-spectacular for automatic OpenAPI schema:

```python
# settings.py
INSTALLED_APPS = [
    ...
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'SummaSaaS API',
    'DESCRIPTION': 'AI-powered text summarization API',
    'VERSION': '1.0.0',
}

# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
]
```

## Testing Requirements

### Unit Tests
- API key authentication
- Request validation
- Rate limiting per tier
- Quota enforcement
- Usage tracking accuracy

### Integration Tests
- Full summarization flow (auth → validate → process → track)
- Error responses (400, 402, 429, 500)
- Multiple modes (extractive, abstractive, hybrid, keywords)
- Concurrent requests

### Coverage Target
Minimum 80% coverage

## Visual QA Handoff

After completion, provide these flows for Visual QA:

1. **API Playground (UI)**
   - Form to enter text
   - Select mode dropdown
   - Submit button
   - Loading spinner during processing
   - Summary displayed on success

2. **Success State**
   - Summary text visible
   - Mode indicator
   - Characters used counter
   - Current usage stats

3. **Error States**
   - 400: Invalid input (show field errors)
   - 402: Quota exceeded (show upgrade prompt)
   - 429: Rate limit hit (show retry timer)
   - 500: Processing failed (show error message)

4. **Usage Dashboard**
   - Chart showing usage over time
   - Current month statistics
   - Quota remaining indicator
   - API call count

## Acceptance Criteria

- [ ] `/api/v1/summarize` endpoint functional
- [ ] API key authentication working
- [ ] All 4 modes (extractive, abstractive, hybrid, keywords) working
- [ ] Rate limiting enforced per tier
- [ ] Quota enforcement returns 402 when exceeded
- [ ] Usage tracking accurate
- [ ] API documentation (Swagger UI) accessible
- [ ] Response times <500ms (excluding model processing)
- [ ] All tests passing (>80% coverage)

## Dependencies
```txt
djangorestframework==3.14.0
drf-spectacular==0.27.0
django-filter==23.5
django-ratelimit==4.1.0
```

## Response Examples

### Successful Summarization
```json
{
  "summary": "This is the generated summary...",
  "mode": "abstractive",
  "characters_used": 1523,
  "usage": {
    "month": "2025-10",
    "characters_used": 45230,
    "character_limit": 100000,
    "percentage_used": 45.23,
    "api_calls_made": 127
  }
}
```

### Quota Exceeded (402)
```json
{
  "error": "Quota exceeded",
  "message": "You've used 100% of your monthly character limit. Upgrade your plan to continue.",
  "usage": {
    "month": "2025-10",
    "characters_used": 100000,
    "character_limit": 100000,
    "percentage_used": 100.0
  },
  "upgrade_url": "/billing/subscribe"
}
```

### Rate Limit (429)
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again in 15 minutes.",
  "retry_after": 900
}
```

## Handoff To
- Web UI Engineer (for playground UI)
- Visual QA Agent (for UI validation)

## Communication Protocol

### On Completion
```
[API_ENGINEER] → [ORCHESTRATOR_AGENT]
ACTION: COMPLETE
TICKET: TICKET-05
STATUS: COMPLETE
ARTIFACTS:
  - src/api/views.py
  - src/api/authentication.py
  - src/api/throttling.py
  - src/api/tests/
TESTS:
  - Passed: 42
  - Coverage: 83%
VISUAL_QA_REQUIRED: YES
NOTES:
  - API docs at /api/v1/docs/
  - All 4 modes tested
  - Rate limiting functional
READY_FOR_NEXT: [TICKET-07]
```

## Important Notes
- Include CORS headers for frontend access
- Log all API errors for monitoring
- Add request ID to responses for debugging
- Implement pagination for history endpoint
- Cache quota checks (avoid DB query per request)
- Use atomic transactions for usage tracking
