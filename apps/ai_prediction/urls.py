from django.urls import path

from .views import PredictRiskAPIView

urlpatterns = [

    path(
        "predict/",
        PredictRiskAPIView.as_view(),
        name="predict-risk",
    ),

]