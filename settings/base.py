# Python modules
import os

from .conf import *  # noqa


# ----------------------------------------------
# Path
#
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_URLCONF = "settings.urls"
WSGI_APPLICATION = "settings.wsgi.application"
ASGI_APPLICATION = "settings.asgi.application"
AUTH_USER_MODEL = 'users.User'

# ----------------------------------------------
# Apps
#
DJANGO_AND_THIRD_PARTY_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
]
PROJECT_APPS = [
    "apps.blog.apps.BlogConfig",
    "apps.users.apps.UsersConfig",
]
INSTALLED_APPS = DJANGO_AND_THIRD_PARTY_APPS + PROJECT_APPS

# ----------------------------------------------
# Middleware | Templates | Validators
#
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "core.middleware.DebugRequestLoggingMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ----------------------------------------------
# Internationalization
#
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ----------------------------------------------
# Static | Media
#
STATIC_URL = "static/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"




# RATELIMIT_VIEW = "pr1.views.ratelimit_view"
RATELIMIT_USE_CACHE = 'default'
