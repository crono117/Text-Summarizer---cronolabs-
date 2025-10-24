from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def profile(request):
    """
    Display the user profile page with account information and subscription status.
    """
    context = {
        'user': request.user,
    }
    return render(request, 'accounts/profile.html', context)
