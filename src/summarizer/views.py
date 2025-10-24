from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import time

from .models import SummarizationTask, SummaryResult
from billing.models import Subscription, UsageQuota, Plan


@login_required
def dashboard(request):
    """
    Dashboard view showing usage statistics and recent summarizations
    """
    user = request.user

    # Get user's current subscription and plan
    try:
        subscription = Subscription.objects.filter(
            user=user,
            status='active'
        ).select_related('plan').first()

        if subscription:
            plan = subscription.plan
        else:
            # Default to FREE plan if no subscription
            plan = Plan.objects.filter(name='FREE').first()
            subscription = None
    except Plan.DoesNotExist:
        plan = None
        subscription = None

    # Get or create current usage quota
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    usage_quota, created = UsageQuota.objects.get_or_create(
        user=user,
        reset_date=last_day_of_month,
        defaults={'characters_used': 0}
    )

    # Calculate usage statistics
    characters_used = usage_quota.characters_used
    character_limit = plan.character_limit if plan else 10000
    characters_remaining = max(0, character_limit - characters_used)
    usage_percentage = (characters_used / character_limit * 100) if character_limit > 0 else 0

    # Get recent summarization tasks
    recent_tasks = SummarizationTask.objects.filter(
        user=user
    ).select_related('result').order_by('-created_at')[:5]

    # Get summary statistics
    total_tasks = SummarizationTask.objects.filter(user=user).count()
    completed_tasks = SummarizationTask.objects.filter(user=user, status='completed').count()
    failed_tasks = SummarizationTask.objects.filter(user=user, status='failed').count()

    # Calculate tasks this month
    tasks_this_month = SummarizationTask.objects.filter(
        user=user,
        created_at__gte=first_day_of_month
    ).count()

    context = {
        'subscription': subscription,
        'plan': plan,
        'plan_name': plan.get_name_display() if plan else 'Free',
        'characters_used': characters_used,
        'character_limit': character_limit,
        'characters_remaining': characters_remaining,
        'usage_percentage': min(100, usage_percentage),
        'recent_tasks': recent_tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'failed_tasks': failed_tasks,
        'tasks_this_month': tasks_this_month,
        'reset_date': usage_quota.reset_date,
    }

    return render(request, 'dashboard/dashboard.html', context)


@login_required
def playground(request):
    """
    Playground view for testing text summarization
    """
    user = request.user
    summary_result = None
    input_text = ''
    mode = 'extractive'
    max_length = 150

    # Get user's plan and usage quota
    try:
        subscription = Subscription.objects.filter(
            user=user,
            status='active'
        ).select_related('plan').first()

        if subscription:
            plan = subscription.plan
        else:
            plan = Plan.objects.filter(name='FREE').first()
    except Plan.DoesNotExist:
        plan = None

    # Get current usage quota
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    usage_quota, created = UsageQuota.objects.get_or_create(
        user=user,
        reset_date=last_day_of_month,
        defaults={'characters_used': 0}
    )

    if request.method == 'POST':
        input_text = request.POST.get('input_text', '').strip()
        mode = request.POST.get('mode', 'extractive')
        max_length = int(request.POST.get('max_length', 150))

        if not input_text:
            messages.error(request, 'Please enter some text to summarize.')
        else:
            character_count = len(input_text)

            # Check if user has enough quota
            if plan and not usage_quota.can_process(character_count, plan):
                messages.error(
                    request,
                    f'Not enough quota. You need {character_count} characters but only have '
                    f'{usage_quota.remaining_characters(plan)} remaining.'
                )
            else:
                # Create summarization task
                task = SummarizationTask.objects.create(
                    user=user,
                    input_text=input_text,
                    mode=mode,
                    max_length=max_length,
                    status='pending'
                )

                # Generate placeholder summary
                # In production, this would call the actual summarization service
                start_time = time.time()

                # Placeholder summarization logic
                placeholder_summary = (
                    f"This is a placeholder summary in {mode} mode. "
                    f"Full NLP-powered summarization functionality coming soon! "
                    f"Your input was {character_count} characters long. "
                    f"The actual summary will be generated using advanced AI models and will be "
                    f"limited to approximately {max_length} words."
                )

                processing_time_ms = int((time.time() - start_time) * 1000)

                # Create summary result
                result = SummaryResult.objects.create(
                    task=task,
                    output_text=placeholder_summary,
                    characters_processed=character_count,
                    processing_time_ms=processing_time_ms
                )

                # Mark task as completed
                task.mark_completed()

                # Update usage quota
                usage_quota.characters_used += character_count
                usage_quota.save()

                summary_result = result
                messages.success(
                    request,
                    f'Summary generated successfully! Processed {character_count} characters in {processing_time_ms}ms.'
                )

    # Calculate remaining quota
    character_limit = plan.character_limit if plan else 10000
    characters_remaining = usage_quota.remaining_characters(plan) if plan else 10000

    context = {
        'input_text': input_text,
        'mode': mode,
        'max_length': max_length,
        'summary_result': summary_result,
        'plan': plan,
        'characters_remaining': characters_remaining,
        'character_limit': character_limit,
        'mode_choices': SummarizationTask.MODE_CHOICES,
    }

    return render(request, 'dashboard/playground.html', context)
