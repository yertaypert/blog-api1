# Django modules
from django.urls import re_path

# Project modules
from apps.notifications.consumers import CommentConsumer


websocket_urlpatterns = [
    re_path(r"ws/posts/(<slug>)/comments/", CommentConsumer.as_asgi()),
]