from rest_framework import serializers


class DashboardSerializer(serializers.Serializer):

    total_records = serializers.IntegerField()

    low_risk = serializers.IntegerField()

    medium_risk = serializers.IntegerField()

    high_risk = serializers.IntegerField()

    model_name = serializers.CharField()

    model_accuracy = serializers.FloatField()