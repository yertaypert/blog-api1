from django.contrib import admin
from django.urls import path, include
from django_ratelimit.decorators import ratelimit
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from rest_framework_simplejwt.views import TokenObtainPairView



urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/', include('apps.blog.urls')),
    path("api/", include("apps.stats.urls")),
    path("api/auth/", include("apps.users.urls")),
    path('api/auth/token/', 
         ratelimit(key='ip', rate='10/m', method='POST', block=True)(TokenObtainPairView.as_view()), 
         name='token_obtain_pair'),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
