from rest_framework import serializers


class PredictionSerializer(serializers.Serializer):

    age = serializers.FloatField()

    gender = serializers.CharField()

    heart_rate = serializers.FloatField()

    systolic_bp = serializers.FloatField()

    temperature = serializers.FloatField()

    spo2 = serializers.FloatField()

    respiratory_rate = serializers.FloatField()

    blood_sugar = serializers.FloatField()

    bmi = serializers.FloatField()

    smoking = serializers.IntegerField()

    exercise_level = serializers.IntegerField()

    cholesterol = serializers.FloatField()

    diastolic_bp = serializers.FloatField()