# Django modules
from django.urls import path

# Django Rest Framework modules
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Project modules
from .views import RegisterView


urlpatterns = [
    path('register/', RegisterView.as_view({'post': 'create'}), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]