from . import verify_user
from rest_framework import status
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from accounts.models import CustomUser, Address
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from .serializers import UserSerializer, AddressSerializer
import json

# Create your views here.
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes((IsAuthenticated,))
@api_view(["GET"])
def current_user_basic(request):
    current_user = request.user.__dict__

    current_user = {
        "user_id": current_user["id"],
        "first_name": current_user["first_name"],
        "is_admin": current_user["is_superuser"],
        "is_blocked": current_user["is_blocked"],
        "wallet_cash": current_user["wallet_cash"],
    }
    print(current_user)
    return Response(current_user)


@authentication_classes([JWTAuthentication])
@permission_classes((IsAuthenticated,))
@api_view(["GET"])
def current_user_full_details(request):
    current_user_id = request.user.id

    current_user = CustomUser.objects.filter(id=current_user_id)
    current_user = UserSerializer(current_user, many=True)

    # current_user_address_id = request.user.__dict__["address_id"]

    current_user_address = Address.objects.filter(user=current_user_id)
    current_user_address = AddressSerializer(current_user_address, many=True)

    print(current_user_id)

    responseData = {
        "user_details": current_user.data,
        "user_address": current_user_address.data,
    }
    return JsonResponse(responseData, safe=False)


class Address_View(APIView):
    permission_classes(
        IsAuthenticated,
    )

    def post(self, request):
        Address_Serialized = AddressSerializer(data=request.data,context={'request': request})

        if Address_Serialized.is_valid():
            Address_Serialized.save()
            return Response(status=status.HTTP_201_CREATED)
        print('add errors :',Address_Serialized.errors)
        return Response(Address_Serialized.errors ,status=status.HTTP_406_NOT_ACCEPTABLE)
    

    def patch(self,request):
        pass

    def put(self,request):
        pass

    


@api_view(["POST"])
def create_user(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        print('data bulu : ',data)
        new_user = CustomUser.objects.create_user(
            first_name = data.get('firstName'),
            last_name = data.get('lastName'),
            email = data.get('email'),
            phone = data.get('phone'),
            password = data.get('password'),
            is_verified=True,
        )

        new_user_address = Address.objects.create(
            user=new_user,
            license = data.get("license"),
            house_name = data.get("house"),
            street = data.get("street"),
            place = data.get("place"),
            city = data.get("city"),
            state = data.get("state"),
            postal_code = data.get("zip_code"),
            land_mark = data.get("landmark"),
            default_address=True
        )
        new_user.save()

        new_user_address.save()

        response_data = {
            "message": "User Created Successfully!",
            "status": status.HTTP_201_CREATED,
        }
        return JsonResponse(response_data)


@authentication_classes([JWTAuthentication])  # EDIT USER
@permission_classes((IsAuthenticated,))
@api_view(["POST"])
def edit_user(request):
    current_user_id = request.user.id

    data = request.data
    print(data)
    current_user = CustomUser.objects.get(id=current_user_id)

    current_user.email = data["email"]
    current_user.first_name = data["firstName"]
    current_user.last_name = data["lastName"]
    current_user.phone = data["phone"]

    current_user.save()

    if data["password"]:
        current_user.set_password(data["password"])
        current_user.save()

    print(current_user_id)
    print(current_user)

    return JsonResponse(status=status.HTTP_202_ACCEPTED)


@api_view(["GET", "POST"])
def get_verification_otp(request):
    if request.method == "GET":
        phone = request.GET.get("phone")
        phone = f"+91{phone}"

        print("phone get", phone)

        verify_user.send(phone)

        response_data = {
            "message": "Otp Send to {phone}!",
            "status": status.HTTP_201_CREATED,
        }
        return JsonResponse(response_data)

    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))["post_data"]
        code = data["code"]
        phone = data["phone"]
        phone = f"+91 {phone}"
        print(code, phone)
        if verify_user.check(phone, code):
            print("User Verified")

        response_data = {
            "message": "Verified!",
            "status": status.HTTP_202_ACCEPTED,
        }
        return JsonResponse(response_data)
