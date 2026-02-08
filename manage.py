import os
import sys
from decouple import config

def main():
    env_id = config("BLOG_ENV_ID", default="local")
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        f"settings.env.{env_id}"
    )

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        raise

    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()