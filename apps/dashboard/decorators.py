"""
View-level decorators for the dashboard application.

Provides role-gating that works with Django's template views
(as opposed to the DRF permission classes used by the API layer).
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from django.http import HttpRequest, HttpResponseForbidden

from apps.users.constants import UserRole


def role_required(*allowed_roles: str) -> Callable:
    """Decorator that restricts a view to users whose role is in *allowed_roles*.

    Usage::

        @login_required
        @role_required(UserRole.DOCTOR, UserRole.ADMIN)
        def my_view(request):
            ...

    Args:
        allowed_roles: One or more ``UserRole`` values.

    Returns:
        The wrapped view, or an ``HttpResponseForbidden`` if the role check fails.
    """

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped(request: HttpRequest, *args: Any, **kwargs: Any):
            user_role = getattr(request.user, "role", None)
            if user_role not in allowed_roles:
                return HttpResponseForbidden(
                    "You do not have permission to access this page."
                )
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
