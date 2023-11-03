from rest_framework import serializers
from accounts.models import Listed_Vehicles
from accounts.models import CustomUser, Address, Order_Details


class ListVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listed_Vehicles
        fields = "__all__"


class ListedVehiclesImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listed_Vehicles
        fields = ""


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ["user"]

    def create(self, validated_data):
        user = self.context["request"].user  # Get the current user from the request

        # Add the user to the validated data
        validated_data["user"] = user
        return Address.objects.create(**validated_data)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order_Details
        fields = "__all__"
