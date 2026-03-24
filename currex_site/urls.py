from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from currex_app.api import CurrencyViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Реєструємо наш ендпоінт
router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Наше API
    path('api/', include(router.urls)),
    
    # Маршрути для Swagger / OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]