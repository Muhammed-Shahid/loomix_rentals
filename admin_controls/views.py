import json
from django.db.models import F ,Q
from rest_framework import status
from django.db.models import Count
from django.shortcuts import render
from django.http import JsonResponse
from django.http import JsonResponse
from default_app.models import Coupon
from default_app.serializers import Coupon_Serializer
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
        data = request.query_params.get('unverified')
        print('data: ',data)
        
        if  data:
            all_vehicles = Listed_Vehicles.objects.filter(Q(is_verified=False) & Q(is_deleted=False))
            serialized_vehicles = ListVehicleSerializer(all_vehicles, many=True)
            return JsonResponse({"all_vehicles": serialized_vehicles.data})
        
        all_vehicles = Listed_Vehicles.objects.filter(is_deleted=False)
        serialized_vehicles = ListVehicleSerializer(all_vehicles, many=True)
        return JsonResponse({"all_vehicles": serialized_vehicles.data})

    return Response(status=status.HTTP_401_UNAUTHORIZED)


@authentication_classes([JWTAuthentication])
@permission_classes((IsAuthenticated,))
@api_view(["PUT"])
def manage_vehicles(request):
    if request.user.is_superuser:
        if request.method == "PUT":
            data = json.loads(request.body.decode("utf-8"))
            vehicle_id = data.get("vehicle_id")
            boolean = data.get("boolean")
            verification_status=data.get('verification_status')
            rejection_cause=data.get('rejection_cause')
            vehicle = Listed_Vehicles.objects.get(id=vehicle_id)
            
            if verification_status==True or verification_status == False:
                vehicle.is_verified = verification_status
                if rejection_cause:
                    vehicle.rejection_cause=rejection_cause
                vehicle.save()
                return Response(status=status.HTTP_200_OK)

            vehicle.blocked = boolean
            vehicle.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        # if request.method=="PATCH":
        #     data = json.loads(request.body.decode("utf-8"))
        #     vehicle_id = data.get("vehicle_id")
        #     pass
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

            user_vehicles = Listed_Vehicles.objects.filter(owner=user)

            for vehicle in user_vehicles:
                vehicle.owner_blocked = boolean
                vehicle.availability = boolean
                vehicle.save()

        return Response("Success")
    return Response(status=status.HTTP_401_UNAUTHORIZED)



@authentication_classes([JWTAuthentication])
@permission_classes((IsAuthenticated,))
@api_view(["GET"])
def view_coupons(request):
    
    all_coupons=Coupon.objects.all()

    all_coupons=Coupon_Serializer(all_coupons,many=True)

    res_data={
        'coupons':all_coupons.data
    }
    return Response(res_data,status=status.HTTP_200_OK)