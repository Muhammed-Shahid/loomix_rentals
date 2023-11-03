from rest_framework import serializers
from .models import VehicleRating


class Review_serializer(serializers.ModelSerializer):
    class Meta:
        model=VehicleRating
        fields = '__all__'