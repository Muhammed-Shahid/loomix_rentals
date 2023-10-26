from django.db.models import F
from rest_framework import status
from django.db.models import Count
from django.shortcuts import render
from django.http import JsonResponse
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from accounts.models import CustomUser, Listed_Vehicles
from rest_framework.decorators import authentication_classes, permission_classes
from accounts.serializers import ListVehicleSerializer,UserSerializer




#  admin_controls/all_users
@api_view(["GET"])
def get_all_users(request):
    #   vehicles = Listed_Vehicles.objects.annotate(number_of_vehicles=Count('owner'))
    #    print(vehicles)

    all_users = CustomUser.objects.all()

    serialized_users = UserSerializer(all_users, many=True)

    print("serialized")

    return JsonResponse({"all_users": serialized_users.data})


@api_view(["GET"])
def get_all_vehicles(request):
    #   vehicles = Listed_Vehicles.objects.annotate(number_of_vehicles=Count('owner'))
    #    print(vehicles)

    all_vehicles = Listed_Vehicles.objects.all()

    serialized_vehicles = ListVehicleSerializer(all_vehicles, many=True)

    print("serialized")

    return JsonResponse({"all_vehicles": serialized_vehicles.data})


@api_view(["PUT", "PATCH"])
def manage_vehicles(request):
    #   vehicles = Listed_Vehicles.objects.annotate(number_of_vehicles=Count('owner'))
    #    print(vehicles)

    if request.method == "PUT":
        vehicle_id = request.POST["vehicle_id"]
        boolean = request.POST["boolean"]

        vehicle = Listed_Vehicles.objects.get(id=vehicle_id)
        vehicle.blocked = boolean

        vehicle.save()
    return Response("Success")


@api_view(["PUT", "PATCH"])
def manage_user(request):
    if request.method == "PUT":
        user_id = request.POST["user_id"]
        boolean = request.POST["boolean"]

        user = CustomUser.objects.get(id=user_id)
        user.is_blocked = boolean

        user.save()
    return Response("Success")
