from django.shortcuts import render

# Create your views here.
def base(request):
    render(request, 'frontend/xbase.html')