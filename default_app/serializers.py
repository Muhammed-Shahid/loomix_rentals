from rest_framework import serializers
from .models import VehicleRating,Coupon


class Review_serializer(serializers.ModelSerializer):
    class Meta:
        model=VehicleRating
        fields = '__all__'

class Coupon_Serializer(serializers.ModelSerializer):
    class Meta:
        model=Coupon
        fields='__all__'