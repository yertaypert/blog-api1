from django.urls import path
from .views import RegisterView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('register/', RegisterView.as_view({'post': 'create'}), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]