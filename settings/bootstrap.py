import os
from settings.conf import ALLOWED_ENV_IDS, ENV_ID, SECRET_KEY


def configure():
    if ENV_ID not in ALLOWED_ENV_IDS:
        raise ValueError(
            f"Invalid ENV_ID '{ENV_ID}'. Must be one of: {ALLOWED_ENV_IDS}"
        )
    if SECRET_KEY == "default-secret-key":
        raise ValueError("BLOG_SECRET_KEY must be set to a real value.")
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        f"settings.env.{ENV_ID}",
    )