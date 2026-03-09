"""
URL routing for the cloud_gateway application.
"""

from django.urls import path

from . import views

app_name = "cloud_gateway"

urlpatterns = [
    path(
        "forward-to-cloud/",
        views.ForwardToCloudView.as_view(),
        name="forward-to-cloud",
    ),
]
