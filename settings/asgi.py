# Python modules
import os

# Django + Third Party modules
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Project modules
from settings.conf import ALLOWED_ENV_IDS, ENV_ID
from apps.notifications.routing import websocket_urlpatterns


assert ENV_ID in ALLOWED_ENV_IDS, f"Invalid ENV_ID: {ENV_ID}. Allowed values are: {ALLOWED_ENV_IDS}"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"settings.env.{ENV_ID}")


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})