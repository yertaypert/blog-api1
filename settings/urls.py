from django.contrib import admin
from django.urls import path, include
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.views import TokenObtainPairView



urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path('api/auth/token/', 
         ratelimit(key='ip', rate='10/m', method='POST', block=True)(TokenObtainPairView.as_view()), 
         name='token_obtain_pair'),
]
