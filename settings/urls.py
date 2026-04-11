# Django modules
from django.contrib import admin
from django.urls import include, path
from django_ratelimit.decorators import ratelimit

# Project modules
from apps.users.views import LoginView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path(
        'api/auth/token/',
        ratelimit(key='ip', rate='10/m', method='POST', block=True)(LoginView.as_view()),
        name='token_obtain_pair',
    ),
    path('api/', include('apps.blog.urls')),
]
