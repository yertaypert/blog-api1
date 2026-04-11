# Django modules
from django.contrib import admin
from django.urls import include, path
from django_ratelimit.decorators import ratelimit

# Project modules
from apps.users.views import LoginView
from apps.users.constants import LOGIN_RATE_LIMIT


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path(
        'api/auth/token/',
        ratelimit(key='ip', rate=LOGIN_RATE_LIMIT, method='POST', block=True)(LoginView.as_view()),
        name='token_obtain_pair',
    ),
    path('api/', include('apps.blog.urls')),
]
