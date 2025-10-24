"""
URL configuration for accounts app.
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Custom profile page
    path('profile/', views.profile, name='profile'),
]
