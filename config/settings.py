import os
from datetime import timedelta
from pathlib import Path

# --- WebSocket Rate Limit (per user per conversation) ---
# Defaults: 5 messages per 10 seconds
WS_RATE_COUNT = int(os.environ.get("WS_RATE_COUNT", "5"))
WS_RATE_WINDOW_SEC = int(os.environ.get("WS_RATE_WINDOW_SEC", "10"))

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.environ.get("DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_prometheus",
    "rest_framework.authtoken",
    "channels",
    "users",
    "chat",
]

MIDDLEWARE = [
    "config.middleware.APILoggingMiddleware",
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    # global fallbacks; scoped throttles below can override by "throttle_scope"
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/min",
        "user": "600/min",
        "conversations": "60/min",      # << temporarily tiny
        "messages-read": "300/min",
        "signup": "10/min",
        "login": "30/min",
    },
}

# Redis cache (for throttling, etc.)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",  # "redis" is the docker-compose service
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "TIMEOUT": None,  # no global TTL
    }
}



ROOT_URLCONF = "config.urls"
ASGI_APPLICATION = "config.asgi.application"

# Templates config (required for admin + our templates/)
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "chat"),
        "USER": os.environ.get("POSTGRES_USER", "chat"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "chat"),
        "HOST": os.environ.get("POSTGRES_HOST", "db"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [(os.environ.get("REDIS_HOST", "redis"), 6379)]},
    }
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "api": {
            "format": (
                '%(asctime)s %(levelname)s '
                'logger=%(name)s '
                'path="%(request_path)s" method=%(request_method)s '
                'status=%(status_code)s '
                'user=%(user)s '
                'msg="%(message)s"'
            )
        },
        "simple": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        }
    },
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "INFO", "propagate": True},
        "chat.ws": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "api.calls": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}


# Allow local overrides for CI/other envs
try:
    from .settings_local import *
except Exception:
    pass
