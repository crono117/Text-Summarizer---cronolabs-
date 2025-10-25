"""
URL configuration for API endpoints
"""

from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # WordPress Integration Endpoints
    path('v1/summarize/', views.summarize, name='summarize'),
    path('v1/seo_description/', views.seo_description, name='seo_description'),
    path('v1/social_caption/', views.social_caption, name='social_caption'),
    path('v1/keywords/', views.keywords, name='keywords'),
    path('v1/usage_status/', views.usage_status, name='usage_status'),
]
