from django.urls import path
from . import views

app_name = 'summarizer'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('playground/', views.playground, name='playground'),
]
