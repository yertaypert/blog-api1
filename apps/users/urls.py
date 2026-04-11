# Django modules
from django.urls import path, include

# Django Rest Framework modules
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Project modules
from .views import RegisterView


router = DefaultRouter()
router.register(r'register', RegisterView, basename='register')

urlpatterns = [
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]