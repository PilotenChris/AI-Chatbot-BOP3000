from rest_framework import serializers


class Feedback(serializers.Serializer):
    question = serializers.CharField()
    response = serializers.CharField()
    feedback = serializers.CharField()
