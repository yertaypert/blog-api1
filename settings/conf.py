# Python modules
import os
from datetime import timedelta
from decouple import Csv, config

# Django modules
from django.utils.log import RequireDebugTrue


# ----------------------------------------------
# Path
#
SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SETTINGS_DIR)

env_path = os.path.join(SETTINGS_DIR, '.env')


# ----------------------------------------------
# Env id
#
SECRET_KEY = config("BLOG_SECRET_KEY", default="default-secret-key", cast=str)
ENV_ID = config("BLOG_ENV_ID", default="local", cast=str)
ALLOWED_ENV_IDS = ("local", "prod",)
ALLOWED_HOSTS = config("BLOG_ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())
EMAIL_BACKEND = config(
    "BLOG_EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
    cast=str,
)

# ----------------------------------------------
# Django REST Framework
#
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}

# ----------------------------------------------
# Simple JWT
#
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=240),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("JWT",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "ON_LOGIN_SUCCESS": "rest_framework_simplejwt.serializers.default_on_login_success",
    "ON_LOGIN_FAILED": "rest_framework_simplejwt.serializers.default_on_login_failed",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

# ----------------------------------------------
# DRF Spectacular
#
SPECTACULAR_SETTINGS = {
    'TITLE': 'Djangorlar API',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# ----------------------------------------------
# Logging
#
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
            'filename': os.path.join(PROJECT_ROOT, 'logs', 'app.log'),
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 3,
            'formatter': 'verbose',
        },
        'debug_requests': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(PROJECT_ROOT, 'logs', 'debug_requests.log'),
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

# ------------------------------------------------
# Redis Configuration
#
REDIS_HOST = config("REDIS_HOST", cast=str, default="localhost")
REDIS_PORT = config("REDIS_PORT", cast=int, default=6379)
REDIS_CELERY_DB = config("REDIS_CELERY_DB", cast=int, default=1)
REDIS_DB = config("REDIS_DB", cast=int, default=2)

REDIS_CELERY_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# ----------------------------------------------
# Caching
#
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# ----------------------------------------------
# Debug Toolbar
#
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.history.HistoryPanel',
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.alerts.AlertsPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.community.CommunityPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

DEBUG = config("BLOG_DEBUG", default=False, cast=bool)
