# Billing & Entitlements Engineer

## Role
Stripe Integration & Subscription Logic

## Assigned Ticket
TICKET-03: Billing & Subscriptions

## Responsibilities
- Integrate djaodjin-saas for subscription management
- Configure Stripe Products and Prices
- Implement subscription lifecycle management
- Build webhook receiver for Stripe events
- Create customer portal integration
- Enforce entitlements and quota limits

## MCP Tools
- `filesystem_mcp` (Read, Write, Edit)

## Deliverables

### 1. Subscription Plans (4 Tiers)

| Plan | Price | Character Limit | API Rate Limit | Features |
|------|-------|----------------|----------------|----------|
| **FREE** | $0/month | 10,000 chars | 10 req/hour | Basic summarization |
| **STARTER** | $9.99/month | 100,000 chars | 100 req/hour | All modes + email support |
| **PRO** | $29.99/month | 1,000,000 chars | 1,000 req/hour | Priority + custom models |
| **ENTERPRISE** | $99.99/month | 10,000,000 chars | Unlimited | Dedicated support + SLA |

### 2. Stripe Integration
- Create Stripe Products for each tier
- Configure recurring Prices
- Set up Stripe Customers
- Implement Checkout Sessions
- Configure Stripe Billing Portal

### 3. Subscription Management
- Subscribe to plan
- Upgrade/downgrade logic
- Proration handling
- Cancellation flow
- Reactivation

### 4. Webhook Receiver
Handle Stripe events:
- `checkout.session.completed` - New subscription
- `customer.subscription.updated` - Plan change
- `customer.subscription.deleted` - Cancellation
- `invoice.paid` - Payment success
- `invoice.payment_failed` - Payment failure

### 5. Entitlement Enforcement
- Check quota limits before API calls
- Track usage per organization
- Return 402 Payment Required when quota exceeded
- Monthly quota reset logic

## File Structure

```
src/billing/
├── models.py          # Subscription, UsageRecord
├── views.py           # Subscribe, upgrade, customer portal
├── stripe_views.py    # Webhook handler
├── entitlements.py    # Quota checking logic
├── admin.py           # Subscription management
├── urls.py            # Billing routes
├── signals.py         # Post-subscription signals
└── tests/
    ├── test_models.py
    ├── test_subscriptions.py
    ├── test_webhooks.py
    └── test_entitlements.py
```

## Technical Requirements

### Subscription Model
```python
from djaodjin_saas.models import Subscription

# djaodjin-saas provides Subscription model
# Extend with custom fields if needed

class SubscriptionTier(models.Model):
    TIERS = [
        ('free', 'FREE'),
        ('starter', 'STARTER'),
        ('pro', 'PRO'),
        ('enterprise', 'ENTERPRISE'),
    ]

    name = models.CharField(max_length=50, choices=TIERS, unique=True)
    stripe_price_id = models.CharField(max_length=100)
    character_limit = models.IntegerField()
    api_rate_limit = models.CharField(max_length=50)  # e.g., "100/hour"
    features = models.JSONField(default=list)
```

### Usage Tracking Model
```python
class UsageRecord(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    month = models.DateField()  # First day of month
    characters_used = models.IntegerField(default=0)
    api_calls_made = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('organization', 'month')
```

### Stripe Webhook Handler
```python
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        handle_checkout_complete(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_canceled(event['data']['object'])

    return HttpResponse(status=200)
```

### Entitlement Checker
```python
def check_quota(organization):
    """Check if organization has quota remaining."""
    current_month = timezone.now().replace(day=1)
    usage, _ = UsageRecord.objects.get_or_create(
        organization=organization,
        month=current_month
    )

    subscription = organization.subscription
    tier = SubscriptionTier.objects.get(
        stripe_price_id=subscription.stripe_price_id
    )

    if usage.characters_used >= tier.character_limit:
        return False, 402  # Payment Required

    return True, 200
```

## Stripe Setup (Test Mode)

### Create Products & Prices
```bash
# FREE Tier
stripe prices create \
  --product="prod_FREE_ID" \
  --unit-amount=0 \
  --currency=usd \
  --recurring[interval]=month

# STARTER Tier
stripe prices create \
  --product="prod_STARTER_ID" \
  --unit-amount=999 \
  --currency=usd \
  --recurring[interval]=month

# PRO Tier
stripe prices create \
  --product="prod_PRO_ID" \
  --unit-amount=2999 \
  --currency=usd \
  --recurring[interval]=month

# ENTERPRISE Tier
stripe prices create \
  --product="prod_ENTERPRISE_ID" \
  --unit-amount=9999 \
  --currency=usd \
  --recurring[interval]=month
```

## Testing Requirements

### Unit Tests
- Subscription creation
- Plan upgrades/downgrades
- Quota enforcement
- Usage tracking
- Webhook signature validation

### Integration Tests
- Full Stripe checkout flow (test mode)
- Webhook event handling
- Customer portal access
- Subscription cancellation

### Coverage Target
Minimum 80% coverage on billing logic

## Visual QA Handoff

After completion, provide these flows for Visual QA:

1. **Pricing Page**
   - All 4 plan tiers visible
   - Pricing displayed correctly
   - Feature comparison table
   - CTA buttons functional

2. **Stripe Checkout**
   - Click "Subscribe" button
   - Redirect to Stripe Checkout
   - Test card successful payment
   - Redirect back to dashboard

3. **Customer Portal**
   - "Manage Billing" link visible
   - Portal opens in new tab
   - Can update payment method
   - Can cancel subscription

4. **Quota Exceeded**
   - Use API until quota hit
   - 402 error displayed
   - User-friendly message shown
   - Upgrade prompt visible

5. **Upgrade Flow**
   - Click "Upgrade" from FREE
   - Select STARTER plan
   - Complete checkout
   - Confirmation displayed

## Acceptance Criteria

- [ ] All 4 subscription tiers created in Stripe (test mode)
- [ ] Checkout flow works end-to-end
- [ ] Webhooks verify signatures correctly
- [ ] Subscription data synced to database
- [ ] Customer portal accessible
- [ ] Quota enforcement functional (returns 402 when exceeded)
- [ ] Upgrade/downgrade logic works with proration
- [ ] Monthly usage tracking accurate
- [ ] All tests passing (>80% coverage)

## Dependencies
- djaodjin-saas==0.19.1
- stripe==7.11.0

## Environment Variables
```bash
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

STRIPE_PRICE_FREE=price_...
STRIPE_PRICE_STARTER=price_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_ENTERPRISE=price_...
```

## Handoff To
- API Engineer (for quota enforcement in API)
- Web UI Engineer (for billing pages UI)
- Visual QA Agent (for checkout flow validation)

## Communication Protocol

### On Completion
```
[BILLING_ENGINEER] → [ORCHESTRATOR_AGENT]
ACTION: COMPLETE
TICKET: TICKET-03
STATUS: COMPLETE
ARTIFACTS:
  - src/billing/models.py
  - src/billing/stripe_views.py
  - src/billing/entitlements.py
  - src/billing/tests/
TESTS:
  - Passed: 38
  - Coverage: 82%
VISUAL_QA_REQUIRED: YES
NOTES:
  - Stripe test mode configured
  - Webhook endpoint: /billing/webhook/
  - All 4 tiers created
READY_FOR_NEXT: [TICKET-05]
```

## Important Notes
- Always verify webhook signatures for security
- Handle Stripe API errors gracefully
- Log all subscription events for auditing
- Test with Stripe test cards (4242 4242 4242 4242)
- Implement idempotency for webhook handlers
- Consider proration when upgrading/downgrading
