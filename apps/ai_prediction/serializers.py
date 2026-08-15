from rest_framework import serializers


class PredictionSerializer(serializers.Serializer):
    age = serializers.FloatField()
    gender = serializers.CharField()
    heart_rate = serializers.FloatField()
    systolic_bp = serializers.FloatField()
    cholesterol = serializers.FloatField()

    def validate_gender(self, value: str) -> str:
        normalized = value.strip().title()
        if normalized not in {"Female", "Male", "0", "1"}:
            raise serializers.ValidationError(
                "Must be Female, Male, 0, or 1."
            )
        return normalized
