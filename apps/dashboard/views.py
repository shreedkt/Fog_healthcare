"""
Server-rendered views for the dashboard application.

Every view delegates business logic to ``DashboardService``.
Templates receive pre-computed context only.
"""

from __future__ import annotations

import logging
from uuid import UUID

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.users.constants import UserRole
from common.constants import ErrorMessages
from common.exceptions import (
    EncryptionError,
    IntegrityVerificationError,
    KeyLoadError,
    RecordNotFoundError,
)

from .decorators import role_required
from .services.dashboard_service import DashboardService

logger = logging.getLogger("apps.dashboard")


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def login_view(request: HttpRequest) -> HttpResponse:
    """Render the login form and process credentials.

    GET  -- display the login page.
    POST -- validate credentials, create session, redirect to home.
    """
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        username: str = request.POST.get("username", "").strip()
        password: str = request.POST.get("password", "")

        if not username or not password:
            messages.error(request, "Both username and password are required.")
            return render(request, "dashboard/login.html", status=400)

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, ErrorMessages.INVALID_CREDENTIALS)
            logger.warning("Failed login attempt for username '%s'.", username)
            return render(
                request,
                "dashboard/login.html",
                {"submitted_username": username},
                status=400,
            )

        login(request, user)
        logger.info("User '%s' logged in via dashboard.", user.username)
        return redirect("dashboard:home")

    return render(request, "dashboard/login.html")


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    """Log the user out and redirect to the login page."""
    username = request.user.username
    logout(request)
    logger.info("User '%s' logged out via dashboard.", username)
    messages.success(request, "You have been logged out.")
    return redirect("dashboard:login")


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------


@login_required
def home_view(request):

    dashboard = DashboardService.get_dashboard()
    return render(

        request,

        "dashboard/home.html",

        {

            "dashboard": dashboard,

        },

    )


# ---------------------------------------------------------------------------
# Records List
# ---------------------------------------------------------------------------

@login_required
@role_required(UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN)
def records_list_view(request: HttpRequest) -> HttpResponse:
    """Paginated table of encrypted medical records.

    Supports optional ``?patient_id=<uuid>`` query parameter for filtering.
    """
    patient_id_filter: str | None = request.GET.get("patient_id", "").strip() or None
    records = DashboardService.list_records(patient_id_filter=patient_id_filter)

    context = {
        "records": records,
        "patient_id_filter": patient_id_filter or "",
    }
    return render(request, "dashboard/records_list.html", context)


# ---------------------------------------------------------------------------
# Record Detail (decrypt + display)
# ---------------------------------------------------------------------------

@login_required
@role_required(UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN)
def record_detail_view(request: HttpRequest, record_id: str) -> HttpResponse:
    """Decrypt and display a single medical record.

    Integrity is verified before decryption.  If verification fails the
    template shows a tamper-warning instead of patient data.
    """
    try:
        uid = UUID(record_id)
    except ValueError:
        messages.error(request, "Invalid record identifier.")
        return redirect("dashboard:records_list")

    try:
        decrypted = DashboardService.get_decrypted_record(
            record_id=uid,
            user=request.user,
            request=request,
        )
        context = {
    "record": decrypted,
    "integrity_ok": True,
    "page": "record_detail",
}

    except RecordNotFoundError:
        messages.error(request, ErrorMessages.RECORD_NOT_FOUND)
        return redirect("dashboard:records_list")

    except IntegrityVerificationError:
        logger.warning(
            "Integrity check failed for record %s (user=%s).",
            record_id,
            request.user.username,
        )
        context = {
            "record": None,
            "integrity_ok": False,
            "record_id": record_id,
        }

    except KeyLoadError as exc:
        logger.error("Key load error: %s", exc)
        messages.error(
            request,
            "Server configuration error. Please contact the administrator.",
        )
        return redirect("dashboard:records_list")

    except EncryptionError as exc:
        logger.error("Decryption error for record %s: %s", record_id, exc)
        messages.error(request, ErrorMessages.DECRYPTION_FAILED)
        return redirect("dashboard:records_list")

    return render(request, "dashboard/record_detail.html", context)
