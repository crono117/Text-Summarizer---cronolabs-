from django.shortcuts import render
from .models import Plan


def pricing(request):
    """
    Display pricing plans for all subscription tiers
    """
    # Get all plans ordered by price
    plans = Plan.objects.all().order_by('monthly_price')

    # Define plan features for display (since JSON is flexible)
    plan_features = {
        'FREE': {
            'features': [
                'Basic summarization',
                '10,000 characters/month',
                '10 API requests/hour',
                'Email support',
                'Community access',
            ],
            'highlight': False,
        },
        'STARTER': {
            'features': [
                'All Free features',
                '100,000 characters/month',
                '100 API requests/hour',
                'Priority email support',
                'Advanced summarization modes',
                'API access',
            ],
            'highlight': False,
        },
        'PRO': {
            'features': [
                'All Starter features',
                '1,000,000 characters/month',
                '1,000 API requests/hour',
                '24/7 priority support',
                'Custom model fine-tuning',
                'Batch processing',
                'Advanced analytics',
            ],
            'highlight': True,  # Most popular
        },
        'ENTERPRISE': {
            'features': [
                'All Pro features',
                'Unlimited characters',
                'Unlimited API requests',
                'Dedicated account manager',
                'Custom integrations',
                'SLA guarantees',
                'On-premise deployment option',
                'Custom contracts',
            ],
            'highlight': False,
        },
    }

    # Combine plan data with features
    plans_with_features = []
    for plan in plans:
        plan_data = {
            'plan': plan,
            'features': plan_features.get(plan.name, {}).get('features', []),
            'highlight': plan_features.get(plan.name, {}).get('highlight', False),
        }
        plans_with_features.append(plan_data)

    context = {
        'plans_with_features': plans_with_features,
    }

    return render(request, 'billing/pricing.html', context)
