from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def base(request):
    return render(request, 'frontend/index.html')