"""
Production settings for Secure Fog Healthcare.

Extends base settings with production-hardened defaults.
"""

from .base import *  # noqa: F401,F403

# ──────────────────────────────────────────────────────────────
# Production Overrides
# ──────────────────────────────────────────────────────────────
DEBUG = False

# Security headers
SECURE_BROWSER_XSS_FILTER: bool = True
SECURE_CONTENT_TYPE_NOSNIFF: bool = True
SECURE_SSL_REDIRECT: bool = True
SECURE_HSTS_SECONDS: int = 31_536_000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = True
SECURE_HSTS_PRELOAD: bool = True

# Cookie security
SESSION_COOKIE_SECURE: bool = True
CSRF_COOKIE_SECURE: bool = True
SESSION_COOKIE_AGE: int = 1800  # 30 minutes

# CSRF trusted origins – set via env for production domain
CSRF_TRUSTED_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")  # noqa: F405
    if origin.strip()
]
