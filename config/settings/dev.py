"""
Development settings for Secure Fog Healthcare.

Extends base settings with development-friendly defaults.
"""

from .base import *  # noqa: F401,F403

# ──────────────────────────────────────────────────────────────
# Development Overrides
# ──────────────────────────────────────────────────────────────
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Allow browsable API in development
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # type: ignore[name-defined]  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# Relax throttling in development
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # type: ignore[name-defined]  # noqa: F405
    "anon": "1000/hour",
    "user": "5000/hour",
}

# CSRF trusted origins for local development
CSRF_TRUSTED_ORIGINS: list[str] = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Session cookie – no secure flag in dev (plain HTTP)
SESSION_COOKIE_SECURE: bool = False
CSRF_COOKIE_SECURE: bool = False
