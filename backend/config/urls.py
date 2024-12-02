# backend/config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/', include('products.urls')),
    path('api/accounts/', include('accounts.urls')),  # accounts 앱 URL    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
