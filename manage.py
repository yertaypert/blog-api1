import os
import sys

from settings.conf import ALLOWED_ENV_IDS, ENV_ID


def main():
    """Run administrative tasks."""
    assert ENV_ID in ALLOWED_ENV_IDS, f"Invalid ENV_ID: {ENV_ID}. Allowed values are {ALLOWED_ENV_IDS}"

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f'settings.env.{ENV_ID}')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()