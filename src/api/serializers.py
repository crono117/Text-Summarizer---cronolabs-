"""
Django REST Framework serializers for API endpoints
"""

from rest_framework import serializers


class SummarizeRequestSerializer(serializers.Serializer):
    """Serializer for summarization requests"""
    text = serializers.CharField(required=True, min_length=10)
    mode = serializers.ChoiceField(
        choices=['extractive', 'abstractive', 'hybrid'],
        default='abstractive'
    )
    max_length = serializers.IntegerField(default=150, min_value=50, max_value=500)
    tone = serializers.ChoiceField(
        choices=['professional', 'casual', 'technical'],
        default='professional',
        required=False
    )


class SEODescriptionRequestSerializer(serializers.Serializer):
    """Serializer for SEO description requests"""
    text = serializers.CharField(required=True, min_length=10)
    max_length = serializers.IntegerField(default=155, min_value=120, max_value=160)
    include_keywords = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )


class SocialCaptionRequestSerializer(serializers.Serializer):
    """Serializer for social media caption requests"""
    text = serializers.CharField(required=True, min_length=10)
    platform = serializers.ChoiceField(
        choices=['twitter', 'linkedin', 'facebook', 'instagram'],
        default='twitter'
    )
    tone = serializers.ChoiceField(
        choices=['engaging', 'professional', 'casual', 'promotional'],
        default='engaging'
    )
    include_emojis = serializers.BooleanField(default=False)
    include_hashtags = serializers.IntegerField(default=3, min_value=0, max_value=10)


class KeywordsRequestSerializer(serializers.Serializer):
    """Serializer for keyword extraction requests"""
    text = serializers.CharField(required=True, min_length=10)
    count = serializers.IntegerField(default=10, min_value=1, max_value=20)
    include_phrases = serializers.BooleanField(default=True)


class APIResponseSerializer(serializers.Serializer):
    """Base serializer for API responses"""
    result = serializers.CharField()
    character_count = serializers.IntegerField()
    quota_used = serializers.IntegerField()
    quota_limit = serializers.IntegerField()
    plan = serializers.CharField()
    timestamp = serializers.DateTimeField()


class SocialCaptionResponseSerializer(APIResponseSerializer):
    """Extended response for social captions with platform limit"""
    platform_limit = serializers.IntegerField()


class KeywordsResponseSerializer(serializers.Serializer):
    """Response serializer for keyword extraction"""
    keywords = serializers.ListField(child=serializers.CharField())
    confidence_scores = serializers.DictField(
        child=serializers.FloatField(),
        required=False
    )
    quota_used = serializers.IntegerField()
    quota_limit = serializers.IntegerField()
    plan = serializers.CharField()
    timestamp = serializers.DateTimeField()


class UsageStatusResponseSerializer(serializers.Serializer):
    """Response serializer for usage status endpoint"""
    plan = serializers.CharField()
    plan_display_name = serializers.CharField()
    quota_used = serializers.IntegerField()
    quota_limit = serializers.IntegerField()
    quota_percentage = serializers.FloatField()
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    days_remaining = serializers.IntegerField()
    rate_limit_per_hour = serializers.IntegerField()
    requests_this_hour = serializers.IntegerField()
    features = serializers.DictField()


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses"""
    detail = serializers.CharField()
    message = serializers.CharField()
    quota_used = serializers.IntegerField(required=False)
    quota_limit = serializers.IntegerField(required=False)
    plan = serializers.CharField(required=False)
    upgrade_url = serializers.URLField(required=False)
