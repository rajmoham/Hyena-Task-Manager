from django.shortcuts import render
from tasks.helpers import login_prohibited

@login_prohibited
def home(request):
    """Display the application's start/home screen."""
    return render(request, 'home.html')

def custom_404(request, exception):
    """Display error page"""
    return render(request, '404.html', status = 404)
