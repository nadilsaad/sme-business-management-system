from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

def home(request):
    return JsonResponse({"message": "SME Business Management System API is running"})

urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("api/", include("business.urls")),
]
