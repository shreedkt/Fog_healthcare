"""
Root URL Configuration for Secure Fog Healthcare.

All API endpoints are versioned under /api/v1/.
"""

from django.contrib import admin
from django.urls import include, path

from apps.cloud_gateway.views import ForwardToCloudView

urlpatterns = [

    # ---------------------------------------------------------
    # Django Admin
    # ---------------------------------------------------------
    path(
        "admin/",
        admin.site.urls,
    ),

    # ---------------------------------------------------------
    # Authentication APIs
    # ---------------------------------------------------------
    path(
        "api/v1/auth/",
        include(("apps.users.urls", "users"), namespace="users"),
    ),

    # ---------------------------------------------------------
    # Medical Records APIs
    # ---------------------------------------------------------
    path(
        "api/v1/records/",
        include(
            ("apps.medical_records.urls", "medical_records"),
            namespace="medical_records",
        ),
    ),

    # ---------------------------------------------------------
    # AI Prediction APIs
    # ---------------------------------------------------------
    path(
        "api/v1/ai/",
        include(
            ("apps.ai_prediction.urls", "ai_prediction"),
            namespace="ai_prediction",
        ),
    ),

    # ---------------------------------------------------------
    # Forward Medical Record to Cloud
    # ---------------------------------------------------------
    path(
        "api/v1/records/forward-to-cloud/",
        ForwardToCloudView.as_view(),
        name="forward-to-cloud",
    ),

    # ---------------------------------------------------------
    # Cloud Gateway APIs
    # ---------------------------------------------------------
    path(
        "api/v1/cloud/",
        include(
            ("apps.cloud_gateway.urls", "cloud_gateway"),
            namespace="cloud_gateway",
        ),
    ),

    # ---------------------------------------------------------
    # Dashboard
    # ---------------------------------------------------------
    path(
        "",
        include(
            ("apps.dashboard.urls", "dashboard"),
            namespace="dashboard",
        ),
    ),

]