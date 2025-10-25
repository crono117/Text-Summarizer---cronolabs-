"""
API views for WordPress integration and external access
"""

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta

from .decorators import require_api_key, enforce_quota_and_rate_limit, log_api_request
from .serializers import (
    SummarizeRequestSerializer,
    SEODescriptionRequestSerializer,
    SocialCaptionRequestSerializer,
    KeywordsRequestSerializer,
    APIResponseSerializer,
    SocialCaptionResponseSerializer,
    KeywordsResponseSerializer,
    UsageStatusResponseSerializer
)
from billing.models import Subscription, Plan
from accounts.models import User


# Platform-specific character limits
PLATFORM_LIMITS = {
    'twitter': 280,
    'linkedin': 1300,  # But recommend ~150 for feed preview
    'facebook': 500,
    'instagram': 2200
}


def generate_summary(text, mode='abstractive', max_length=150, tone='professional'):
    """
    Generate a summary of the input text.

    This is a placeholder implementation. In production, this would:
    - Use BART or T5 models for abstractive summarization
    - Use TextRank for extractive summarization
    - Combine both for hybrid mode

    Args:
        text: Input text to summarize
        mode: Summarization mode (extractive, abstractive, hybrid)
        max_length: Maximum length in words
        tone: Tone of the summary

    Returns:
        str: Generated summary
    """
    # Placeholder implementation - replace with actual NLP model
    word_count = len(text.split())
    sentences = text.split('.')[:3]  # Take first 3 sentences as simple summary
    simple_summary = '. '.join(sentences).strip()

    if mode == 'extractive':
        # In production: Use TextRank or similar sentence ranking
        return simple_summary + '.'
    elif mode == 'abstractive':
        # In production: Use BART/T5 model
        return f"This article discusses {simple_summary.lower()[:100]}... [Generated using {mode} mode with {tone} tone]"
    else:  # hybrid
        # In production: Combine extractive + abstractive
        return f"{simple_summary}. [Hybrid summary combining key sentences and paraphrasing]"


def generate_seo_description(text, max_length=155, include_keywords=None):
    """
    Generate SEO-optimized meta description.

    Args:
        text: Input text
        max_length: Maximum character count (typically 155 for SEO)
        include_keywords: Optional list of keywords to emphasize

    Returns:
        str: SEO-optimized description
    """
    # Placeholder - in production, use T5 or similar with SEO-specific prompting
    words = text.split()[:20]
    description = ' '.join(words)

    if include_keywords and len(include_keywords) > 0:
        description = f"{', '.join(include_keywords[:2])}: {description}"

    # Truncate to max_length
    if len(description) > max_length:
        description = description[:max_length-3] + '...'

    return description


def generate_social_caption(text, platform='twitter', tone='engaging',
                           include_emojis=False, include_hashtags=3):
    """
    Generate platform-optimized social media caption.

    Args:
        text: Input text
        platform: Target platform (twitter, linkedin, facebook, instagram)
        tone: Caption tone (engaging, professional, casual, promotional)
        include_emojis: Whether to include emojis
        include_hashtags: Number of hashtags to include

    Returns:
        str: Platform-optimized caption
    """
    # Placeholder - in production, use T5/GPT with platform-specific prompting
    sentences = text.split('.')[:2]
    base_caption = ' '.join(sentences).strip()

    platform_limit = PLATFORM_LIMITS.get(platform, 280)
    caption = base_caption[:platform_limit - 50]  # Leave room for hashtags/emojis

    if include_emojis and platform in ['twitter', 'instagram']:
        caption = f"🚀 {caption}"

    if include_hashtags > 0:
        hashtags = ['#ContentMarketing', '#AI', '#Productivity', '#Marketing', '#Technology'][:include_hashtags]
        caption += ' ' + ' '.join(hashtags)

    # Trim to platform limit
    if len(caption) > platform_limit:
        caption = caption[:platform_limit-3] + '...'

    return caption


def extract_keywords(text, count=10, include_phrases=True):
    """
    Extract keywords and phrases from text.

    Args:
        text: Input text
        count: Number of keywords to extract
        include_phrases: Whether to include multi-word phrases

    Returns:
        tuple: (list of keywords, dict of confidence scores)
    """
    # Placeholder - in production, use RAKE, YAKE, or KeyBERT
    words = text.lower().split()

    # Simple frequency-based extraction (placeholder)
    word_freq = {}
    for word in words:
        if len(word) > 4:  # Filter short words
            word_freq[word] = word_freq.get(word, 0) + 1

    # Get top keywords by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, freq in sorted_words[:count]]

    # Generate confidence scores (placeholder)
    confidence_scores = {word: min(1.0, freq / 10) for word, freq in sorted_words[:count]}

    return keywords, confidence_scores


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@require_api_key
@enforce_quota_and_rate_limit
@log_api_request
def summarize(request):
    """
    POST /api/v1/summarize/

    Generate a TL;DR summary of the input text.
    """
    serializer = SummarizeRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    text = data['text']
    mode = data['mode']
    max_length = data['max_length']
    tone = data.get('tone', 'professional')

    # Generate summary
    summary = generate_summary(text, mode, max_length, tone)

    # Get user's quota information
    user = request.user

    # Get account and subscription
    account = user.owned_accounts.first() or (
        user.account_memberships.first().account
        if user.account_memberships.exists()
        else None
    )

    if account:
        try:
            plan = account.subscription.plan
        except Subscription.DoesNotExist:
            plan = Plan.objects.filter(code='FREE').first()
    else:
        plan = Plan.objects.filter(code='FREE').first()

    response_data = {
        'result': summary,
        'character_count': len(text),
        'quota_used': user.monthly_char_used,
        'quota_limit': plan.char_limit,
        'plan': plan.code,
        'timestamp': timezone.now()
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@require_api_key
@enforce_quota_and_rate_limit
@log_api_request
def seo_description(request):
    """
    POST /api/v1/seo_description/

    Generate an SEO-optimized meta description.
    """
    serializer = SEODescriptionRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    text = data['text']
    max_length = data['max_length']
    include_keywords = data.get('include_keywords', [])

    # Generate SEO description
    description = generate_seo_description(text, max_length, include_keywords)

    # Get user's quota information
    user = request.user

    # Get account and subscription
    account = user.owned_accounts.first() or (
        user.account_memberships.first().account
        if user.account_memberships.exists()
        else None
    )

    if account:
        try:
            plan = account.subscription.plan
        except Subscription.DoesNotExist:
            plan = Plan.objects.filter(code='FREE').first()
    else:
        plan = Plan.objects.filter(code='FREE').first()

    response_data = {
        'result': description,
        'character_count': len(description),
        'quota_used': user.monthly_char_used,
        'quota_limit': plan.char_limit,
        'plan': plan.code,
        'timestamp': timezone.now()
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@require_api_key
@enforce_quota_and_rate_limit
@log_api_request
def social_caption(request):
    """
    POST /api/v1/social_caption/

    Generate a platform-optimized social media caption.
    """
    serializer = SocialCaptionRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    text = data['text']
    platform = data['platform']
    tone = data['tone']
    include_emojis = data['include_emojis']
    include_hashtags = data['include_hashtags']

    # Generate caption
    caption = generate_social_caption(text, platform, tone, include_emojis, include_hashtags)

    # Get user's quota information
    user = request.user

    # Get account and subscription
    account = user.owned_accounts.first() or (
        user.account_memberships.first().account
        if user.account_memberships.exists()
        else None
    )

    if account:
        try:
            plan = account.subscription.plan
        except Subscription.DoesNotExist:
            plan = Plan.objects.filter(code='FREE').first()
    else:
        plan = Plan.objects.filter(code='FREE').first()

    response_data = {
        'result': caption,
        'character_count': len(caption),
        'platform_limit': PLATFORM_LIMITS.get(platform, 280),
        'quota_used': user.monthly_char_used,
        'quota_limit': plan.char_limit,
        'plan': plan.code,
        'timestamp': timezone.now()
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@require_api_key
@enforce_quota_and_rate_limit
@log_api_request
def keywords(request):
    """
    POST /api/v1/keywords/

    Extract keywords and key phrases from text.
    """
    serializer = KeywordsRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    text = data['text']
    count = data['count']
    include_phrases = data['include_phrases']

    # Extract keywords
    extracted_keywords, confidence_scores = extract_keywords(text, count, include_phrases)

    # Get user's quota information
    user = request.user

    # Get account and subscription
    account = user.owned_accounts.first() or (
        user.account_memberships.first().account
        if user.account_memberships.exists()
        else None
    )

    if account:
        try:
            plan = account.subscription.plan
        except Subscription.DoesNotExist:
            plan = Plan.objects.filter(code='FREE').first()
    else:
        plan = Plan.objects.filter(code='FREE').first()

    response_data = {
        'keywords': extracted_keywords,
        'confidence_scores': confidence_scores,
        'quota_used': user.monthly_char_used,
        'quota_limit': plan.char_limit,
        'plan': plan.code,
        'timestamp': timezone.now()
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
@require_api_key
def usage_status(request):
    """
    GET /api/v1/usage_status/

    Retrieve current usage statistics and plan information.
    """
    user = request.user

    # Get account and subscription
    account = user.owned_accounts.first() or (
        user.account_memberships.first().account
        if user.account_memberships.exists()
        else None
    )

    if account:
        try:
            plan = account.subscription.plan
        except Subscription.DoesNotExist:
            plan = Plan.objects.filter(code='FREE').first()
    else:
        plan = Plan.objects.filter(code='FREE').first()

    if not plan:
        return Response({
            'detail': 'no_plan_found',
            'message': 'No billing plan found for user'
        }, status=status.HTTP_404_NOT_FOUND)

    # Calculate stats
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    days_remaining = (last_day_of_month - today).days

    quota_percentage = (user.monthly_char_used / plan.char_limit * 100) if plan.char_limit > 0 else 0

    # Get rate limit info
    current_hour = timezone.now().replace(minute=0, second=0, microsecond=0)
    cache_key = f"rate_limit:{user.id}:{current_hour.isoformat()}"
    requests_this_hour = cache.get(cache_key, 0)

    # Build features dict based on plan code
    features = {
        'extractive_summarization': True,
        'abstractive_summarization': plan.code != 'FREE',
        'hybrid_summarization': plan.code in ['PRO', 'ENTERPRISE'],
        'keyword_extraction': True,
        'seo_optimization': True,
        'social_captions': True,
        'api_access': True,
        'priority_support': plan.priority_support,
    }

    response_data = {
        'plan': plan.code,
        'plan_display_name': f"{plan.display_name} (${plan.monthly_price_usd}/month)",
        'quota_used': user.monthly_char_used,
        'quota_limit': plan.char_limit,
        'quota_percentage': round(quota_percentage, 1),
        'period_start': first_day_of_month,
        'period_end': last_day_of_month,
        'days_remaining': days_remaining,
        'rate_limit_per_hour': plan.req_per_hour,
        'requests_this_hour': requests_this_hour,
        'features': features
    }

    return Response(response_data, status=status.HTTP_200_OK)
