from pathlib import Path
from .conf import SECRET_KEY, DEBUG, ALLOWED_HOSTS, EMAIL_BACKEND   
import os
from django.utils.log import RequireDebugTrue
from datetime import timedelta


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = SECRET_KEY
DEBUG = DEBUG
ALLOWED_HOSTS = ALLOWED_HOSTS
EMAIL_BACKEND = EMAIL_BACKEND


ROOT_URLCONF = "settings.urls"
WSGI_APPLICATION = "settings.wsgi.application"
ASGI_APPLICATION = "settings.asgi.application"
AUTH_USER_MODEL = 'users.User'

DEFAULT_FROM_EMAIL = "noreply@blog.local"

LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)


DJANGO_AND_THIRD_PARTY_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
]

PROJECT_APPS = [
    "apps.blog",
    "apps.users",
    "apps.stats",
]

INSTALLED_APPS = DJANGO_AND_THIRD_PARTY_APPS + PROJECT_APPS


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.core.middleware.LanguageDetectionMiddleware",
    "apps.core.timezone_middleware.UserTimezoneMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

# ----------------------------------------------
# Database
#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
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
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ----------------------------------------------
# REST Framework
#
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',

    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ----------------------------------------------
# Simple JWT
#
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
}

# ----------------------------------------------
# Spectacular
#
SPECTACULAR_SETTINGS = {
    'TITLE': 'My Blog API',
    'DESCRIPTION': 'API documentation for all endpoints: Auth, Posts, Comments, Stats. Includes cache, Redis events, emails, timezone/language behavior.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': r'/api',
    'SWAGGER_UI_DIST': 'SIDECAR',  
    'REDOC_DIST': 'SIDECAR',
}

# ----------------------------------------------
# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'simple': {
            'format': '%(levelname)s: %(message)s',
        },
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s (%(module)s): %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },

    'filters': {
        'require_debug_true': {
            '()': RequireDebugTrue,
        },
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'app.log',
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 3,
            'formatter': 'verbose',
        },
        'debug_requests': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'debug_requests.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 3,
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
    },

    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'users': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'blog': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'debug_requests': {
            'handlers': ['debug_requests'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Caches
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}



# RATELIMIT_VIEW = "pr1.views.ratelimit_view"
RATELIMIT_USE_CACHE = 'default'


# ----------------------------------------------
# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"

LANGUAGES = [
    ("en", "English"),
    ("ru", "Russian"),
    ("kk", "Kazakh"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"