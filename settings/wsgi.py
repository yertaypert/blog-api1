import os

from django.core.wsgi import get_wsgi_application

from settings.conf import ALLOWED_ENV_IDS, ENV_ID


assert ENV_ID in ALLOWED_ENV_IDS, f"Invalid ENV_ID: {ENV_ID}. Allowed values are: {ALLOWED_ENV_IDS}"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"settings.env.{ENV_ID}")

application = get_wsgi_application()
