from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from .serializers import PredictionSerializer
from .services import AIPredictionService


class PredictRiskAPIView(APIView):

    authentication_classes = []

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = PredictionSerializer(data=request.data)

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        patient_data = serializer.validated_data

        service = AIPredictionService()

        prediction = service.predict(patient_data)

        return Response(
            prediction,
            status=status.HTTP_200_OK,
        )