"""
Root URL configuration for Secure Fog Healthcare.

All API endpoints are versioned under /api/v1/.
"""

from django.contrib import admin
from django.urls import include, path

from apps.cloud_gateway.views import ForwardToCloudView

urlpatterns: list = [
    path("admin/", admin.site.urls),
    # API (DRF)
    path("api/v1/auth/", include("apps.users.urls", namespace="users")),
    path("api/v1/records/", include("apps.medical_records.urls", namespace="medical_records")),
    path("api/v1/records/forward-to-cloud/", ForwardToCloudView.as_view(), name="forward-to-cloud"),
    path("api/v1/cloud/", include("apps.cloud_gateway.urls", namespace="cloud_gateway")),
    # Dashboard (server-rendered) -- mounted at root, placed last to avoid shadowing /api/ and /admin/
    path("", include("apps.dashboard.urls", namespace="dashboard")),
]
