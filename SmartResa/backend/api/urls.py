# api/urls.py
from django.urls import path
from . import views
from django.urls import path
from .views import rfid_access_check
urlpatterns = [
    # We'll add actual endpoints later
    path('test/', views.test_api, name='test-api'),
    path('rfid/access/', rfid_access_check, name='rfid_access'),
]

# api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def test_api(request):
    return Response({"status": "API working!"})