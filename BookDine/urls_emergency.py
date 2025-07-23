"""
Emergency minimal URLs - No dependencies
"""
from django.http import HttpResponse
from django.urls import path

def home(request):
    return HttpResponse("""
    <h1>BookDine Emergency Mode</h1>
    <p>App is running in emergency mode</p>
    <p>Missing dependency: django-cors-headers</p>
    """, content_type="text/html")

def health(request):
    return HttpResponse("OK", content_type="text/plain")

urlpatterns = [
    path('', home, name='home'),
    path('health/', health, name='health'),
]