"""
URL routing for the dashboard application.
"""

from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.home_view, name="home"),
    path("records/", views.records_list_view, name="records_list"),
    path("records/<str:record_id>/", views.record_detail_view, name="record_detail"),
]
