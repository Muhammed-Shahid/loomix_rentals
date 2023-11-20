import json
from . import verify_user
from django.db.models import Q
from rest_framework import status
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, AddressSerializer
from accounts.models import CustomUser, Address, Order_Details
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes, permission_classes


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

    current_user_address = Address.objects.filter(
        Q(user=current_user_id) & Q(is_deleted=False)
    )
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
        Address_Serialized = AddressSerializer(
            data=request.data, context={"request": request}
        )

        if Address_Serialized.is_valid():
            Address_Serialized.save()
            return Response(status=status.HTTP_201_CREATED)
        print("add errors :", Address_Serialized.errors)
        return Response(
            Address_Serialized.errors, status=status.HTTP_406_NOT_ACCEPTABLE
        )

    def patch(self, request):
        data = request.data
        address_id = data["address_id"]

        EditableAddress = Address.objects.get(id=address_id)
        user_id = request.user.id
        user = CustomUser.objects.get(id=user_id)
        if data["make_default"] == True:
            current_default_address = Address.objects.get(
                Q(user=user) & Q(default_address=True)
            )
            if current_default_address:
                current_default_address.default_address = False
                current_default_address.save()
            EditableAddress.default_address = True
            EditableAddress.save()
            return Response(status=status.HTTP_200_OK)

        if data["address_data"]:
            address_data = data["address_data"]

            EditableAddress.house_name = address_data["house_name"]
            EditableAddress.street = address_data["street"]
            EditableAddress.place = address_data["place"]
            EditableAddress.city = address_data["city"]
            EditableAddress.state = address_data["state"]
            EditableAddress.postal_code = address_data["postal_code"]
            EditableAddress.land_mark = address_data["land_mark"]
            EditableAddress.phone = address_data["phone"]

            EditableAddress.save()

            return Response(status=status.HTTP_200_OK)

    def put(self, request):
        address_id = request.data["address_id"]
        print("address id", address_id)
        user = CustomUser.objects.get(id=request.user.id)
        incomplete_orders = Order_Details.objects.filter(
            Q(shipping_address_id=address_id)
            & ~Q(order_status="Delivered")
            & ~Q(order_status="Cancelled")
        )

        print(incomplete_orders)
        if incomplete_orders:
            return Response(status=status.HTTP_226_IM_USED)

        address = Address.objects.get(id=address_id)
        address.is_deleted = True
        address.default_address = False
        address.save()

        address_remaining = Address.objects.filter(Q(user=user) & Q(is_deleted=False))
        address_count = address_remaining.count()
        if address_count == 1:
            address_remaining = Address.objects.get(Q(user=user) & Q(is_deleted=False))
            address_remaining.default_address = True
            address_remaining.save()
        return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def create_user(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        print("data bulu : ", data)
        new_user = CustomUser.objects.create_user(
            first_name=data.get("firstName"),
            last_name=data.get("lastName"),
            email=data.get("email"),
            phone=data.get("phone"),
            password=data.get("password"),
            is_verified=True,
        )

        new_user_address = Address.objects.create(
            user=new_user,
            license=data.get("license"),
            house_name=data.get("house"),
            street=data.get("street"),
            place=data.get("place"),
            city=data.get("city"),
            state=data.get("state"),
            postal_code=data.get("zip_code"),
            land_mark=data.get("landmark"),
            default_address=True,
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
        data = json.loads(request.body.decode("utf-8"))["post_data"]
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
        return Response(status=status.HTTP_417_EXPECTATION_FAILED)


@api_view(["GET", "POST"])
def reset_password(request):
    if request.method == "GET":
        phone = request.GET.get("phone")
        email = request.GET.get("email")

        try:
            user = CustomUser.objects.get(Q(phone=phone) & Q(email=email))

        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_200_OK)

    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))["params"]
        email = data["email"]
        phone = data["phone"]
        new_password = data["new_password"]

        user = CustomUser.objects.get(Q(phone=phone) & Q(email=email))

        user.set_password(new_password)

        user.save()

        return Response(status=status.HTTP_200_OK)
