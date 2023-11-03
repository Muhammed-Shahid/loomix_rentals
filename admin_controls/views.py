import json
from django.db.models import F
from rest_framework import status
from django.db.models import Count
from django.shortcuts import render
from django.http import JsonResponse
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from accounts.models import CustomUser, Listed_Vehicles
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from accounts.serializers import ListVehicleSerializer, UserSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication


#  admin_controls/all_users
@authentication_classes([JWTAuthentication])
@permission_classes((IsAuthenticated,))
@api_view(["GET"])
def get_all_users(request):
    #   vehicles = Listed_Vehicles.objects.annotate(number_of_vehicles=Count('owner'))
    #    print(vehicles)

    if request.user.is_superuser:
        all_users = CustomUser.objects.all()

        serialized_users = UserSerializer(all_users, many=True)

        print("serialized")

        return JsonResponse({"all_users": serialized_users.data})
    return Response(status=status.HTTP_401_UNAUTHORIZED)


@authentication_classes([JWTAuthentication])
@permission_classes((IsAuthenticated,))
@api_view(["GET"])
def get_all_vehicles(request):
    if request.user.is_superuser:
        all_vehicles = Listed_Vehicles.objects.all()

        serialized_vehicles = ListVehicleSerializer(all_vehicles, many=True)

        print("serialized")

        return JsonResponse({"all_vehicles": serialized_vehicles.data})
    return Response(status=status.HTTP_401_UNAUTHORIZED)


@authentication_classes([JWTAuthentication])
@permission_classes((IsAuthenticated,))
@api_view(["PUT", "PATCH"])
def manage_vehicles(request):
    if request.user.is_superuser:
        if request.method == "PUT":
            data = json.loads(request.body.decode("utf-8"))
            vehicle_id = data.get("vehicle_id")
            boolean = data.get("boolean")

            vehicle = Listed_Vehicles.objects.get(id=vehicle_id)
            vehicle.blocked = boolean

            vehicle.save()
        return Response("Success")
    return Response(status=status.HTTP_401_UNAUTHORIZED)


@authentication_classes([JWTAuthentication])
@permission_classes((IsAuthenticated,))
@api_view(["PUT", "PATCH"])
def manage_user(request):
    if request.user.is_superuser:
        if request.method == "PUT":
            data = json.loads(request.body.decode("utf-8"))

            # Access the values from the JSON data
            user_id = data.get("user_id")
            boolean = data.get("boolean")

            user = CustomUser.objects.get(id=user_id)
            user.is_blocked = boolean

            user.save()
        return Response("Success")
    return Response(status=status.HTTP_401_UNAUTHORIZED)
