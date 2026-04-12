# Django modules
from django.urls import path, include

# Project modules
from apps.notifications.views import post_stream


urlpatterns = [
    path("api/posts/stream/", post_stream),
]