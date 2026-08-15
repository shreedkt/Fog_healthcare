"""
URL routing for the medical_records application.
"""

from django.urls import path

from . import views

app_name = "medical_records"

urlpatterns = [
    path("create/", views.RecordCreateView.as_view(), name="record-create"),
    path("<uuid:record_id>/", views.RecordDetailView.as_view(), name="record-detail"),
    path(
        "patient/<uuid:patient_id>/",
        views.PatientRecordsView.as_view(),
        name="patient-records",
    ),
]
