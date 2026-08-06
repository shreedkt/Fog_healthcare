"""
Base settings for Secure Fog-Based Healthcare Data Sharing.

Common configuration shared across all environments.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────────
# Path Configuration
# ──────────────────────────────────────────────────────────────
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# ──────────────────────────────────────────────────────────────
# Core Django Settings
# ──────────────────────────────────────────────────────────────
SECRET_KEY: str = os.getenv("DJANGO_SECRET_KEY", "CHANGE-ME")
DEBUG: bool = os.getenv("DJANGO_DEBUG", "False").lower() in ("true", "1", "yes")

ALLOWED_HOSTS: list[str] = [
    h.strip()
    for h in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost").split(",")
    if h.strip()
]

# ──────────────────────────────────────────────────────────────
# Application Definition
# ──────────────────────────────────────────────────────────────
DJANGO_APPS: list[str] = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS: list[str] = [
    "rest_framework",
]

LOCAL_APPS: list[str] = [
    "apps.users",
    "apps.encryption",
    "apps.medical_records",
    "apps.audit",
    "apps.cloud_gateway",
    "apps.dashboard",
     "apps.ai_prediction",
]

INSTALLED_APPS: list[str] = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ──────────────────────────────────────────────────────────────
# Middleware
# ──────────────────────────────────────────────────────────────
MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF: str = "config.urls"

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

WSGI_APPLICATION: str = "config.wsgi.application"

# ──────────────────────────────────────────────────────────────
# Database
# ──────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "fog_healthcare"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ──────────────────────────────────────────────────────────────
# Custom User Model
# ──────────────────────────────────────────────────────────────
AUTH_USER_MODEL: str = "users.User"

# ──────────────────────────────────────────────────────────────
# Password Validation
# ──────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ──────────────────────────────────────────────────────────────
# Internationalization
# ──────────────────────────────────────────────────────────────
LANGUAGE_CODE: str = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N: bool = True
USE_TZ: bool = True

# ──────────────────────────────────────────────────────────────
# Static Files
# ──────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ──────────────────────────────────────────────────────────────
# Default Primary Key
# ──────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

# ──────────────────────────────────────────────────────────────
# Django REST Framework
# ──────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.getenv("RATE_LIMIT_ANON", "20/hour"),
        "user": os.getenv("RATE_LIMIT_USER", "100/hour"),
    },
    "DEFAULT_RENDERER_CLASSES": [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "EXCEPTION_HANDLER": "common.exceptions.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# ──────────────────────────────────────────────────────────────
# Session Configuration
# ──────────────────────────────────────────────────────────────
SESSION_ENGINE: str = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE: int = 3600  # 1 hour
SESSION_COOKIE_HTTPONLY: bool = True
SESSION_COOKIE_SAMESITE: str = "Lax"
SESSION_SAVE_EVERY_REQUEST: bool = True

LOGIN_URL: str = "/login/"
LOGIN_REDIRECT_URL: str = "/"

# ──────────────────────────────────────────────────────────────
# CSRF Configuration
# ──────────────────────────────────────────────────────────────
CSRF_COOKIE_HTTPONLY: bool = False  # DRF needs JS access to read CSRF token
CSRF_COOKIE_SAMESITE: str = "Lax"

# ──────────────────────────────────────────────────────────────
# Cloud Gateway Configuration
# ──────────────────────────────────────────────────────────────
CLOUD_API_URL: str = os.getenv("CLOUD_API_URL", "")
CLOUD_API_TIMEOUT: int = int(os.getenv("CLOUD_API_TIMEOUT", "30"))
CLOUD_API_MAX_RETRIES: int = int(os.getenv("CLOUD_API_MAX_RETRIES", "3"))

# ──────────────────────────────────────────────────────────────
# ECC Key Paths
# ──────────────────────────────────────────────────────────────
FOG_ECC_PRIVATE_KEY_PATH: Path = BASE_DIR / os.getenv(
    "FOG_ECC_PRIVATE_KEY_PATH", "keys/fog_private_key.pem"
)
FOG_ECC_PUBLIC_KEY_PATH: Path = BASE_DIR / os.getenv(
    "FOG_ECC_PUBLIC_KEY_PATH", "keys/fog_public_key.pem"
)
CLOUD_ECC_PUBLIC_KEY_PATH: Path = BASE_DIR / os.getenv(
    "CLOUD_ECC_PUBLIC_KEY_PATH", "keys/cloud_public_key.pem"
)
# ──────────────────────────────────────────────────────────────
# Machine Learning Configuration
# ──────────────────────────────────────────────────────────────

ML_MODEL_DIR: Path = BASE_DIR / "ml_model"
ML_MODEL_DIR.mkdir(exist_ok=True)

RISK_MODEL_PATH: Path = ML_MODEL_DIR / "risk_model.pkl"
SCALER_PATH: Path = ML_MODEL_DIR / "scaler.pkl"

AI_PREDICTION_ENABLED: bool = os.getenv(
    "AI_PREDICTION_ENABLED",
    "True"
).lower() in ("true", "1", "yes")

# ──────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────
LOG_DIR: Path = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },

        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(
                LOG_DIR / os.getenv("LOG_FILE", "fog_healthcare.log").split("/")[-1]
            ),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },

        "security_file": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "security.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },

        # ⭐ AI Prediction Log
        "ai_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "ai_prediction.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
        },
    },

    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },

        "apps": {
            "handlers": ["console", "file"],
            "level": os.getenv("LOG_LEVEL", "DEBUG"),
            "propagate": False,
        },

        "security": {
            "handlers": ["console", "security_file"],
            "level": "WARNING",
            "propagate": False,
        },

        # ⭐ AI Logger
        "apps.ai_prediction": {
            "handlers": ["console", "ai_file"],
            "level": "INFO",
            "propagate": False,
        },
        "ml_training": {
    "handlers": ["console", "ai_file"],
    "level": "INFO",
    "propagate": False,
},
    },
}
