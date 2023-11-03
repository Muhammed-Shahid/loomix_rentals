import os
import pytz
import json
import razorpay

env = os.environ
from datetime import datetime
from django.db.models import Q
from rest_framework import status
from django.db.models import Count
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.views import APIView
from .serializers import Review_serializer
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.decorators import api_view
from accounts.Order_Status import PaymentStatus
from django.db.models.functions import ExtractMonth
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.serializers import ListVehicleSerializer, OrderSerializer
from default_app.models import Cart_Items, VehicleRating, Whishlist, Coupon
from accounts.models import Listed_Vehicles, CustomUser, Order_Details, Address
from rest_framework.decorators import authentication_classes, permission_classes


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart_Items
        fields = "__all__"


class HomeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {
            "message": "Welcome to the JWT Authentication page using React Js and Django!"
        }

        current_user = request.user

        print(current_user)
        return Response(content)


class VehicleView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        location = request.GET.get("location")
        make = request.GET.get("make")
        user_specific = request.GET.get("user_specific")
        vehicle_id = request.GET.get("vehicle_id")
        search_param = request.GET.get("search_param")
        price_range = request.GET.get("price_range")

        if price_range is not None:
            price_range = int(price_range)

        print("price range", price_range)
        current_user_id = request.user.id

        vehicles = Listed_Vehicles.objects.exclude(
            Q(owner=current_user_id) | Q(blocked=True)
        )

        if location:
            vehicles = vehicles.filter(place=location).exclude(
                Q(owner=current_user_id) | Q(blocked=True)
            )

        if make:
            vehicles = vehicles.filter(make=make).exclude(
                Q(owner=current_user_id) | Q(blocked=True)
            )

        if location and make:
            vehicles = vehicles.filter(Q(make=make) and Q(place=location)).exclude(
                Q(owner=current_user_id) | Q(blocked=True)
            )

        if search_param:
            vehicles = vehicles.filter(
                Q(make__icontains=search_param)
                | Q(model__icontains=search_param)
                | Q(place__icontains=search_param)
            )

        if price_range:
            vehicles = vehicles.filter(price__lte=price_range)

        if vehicle_id:
            vehicles = Listed_Vehicles.objects.filter(id=vehicle_id)

        if user_specific:
            print(user_specific)
            current_user_id = request.user.id
            vehicles = Listed_Vehicles.objects.filter(owner=current_user_id)

        serializer = ListVehicleSerializer(vehicles, many=True)

        # paginator = Paginator(serializer.data, 8)
        makes = Listed_Vehicles.objects.values_list("make", flat=True)
        locations = Listed_Vehicles.objects.values_list("place", flat=True)

        response_data = {
            "vehicles": serializer.data,
            "makes": list(makes),
            "locations": list(locations),
        }

        return Response(response_data)

    def post(self, request, *args, **kwargs):
        vehicle_serializer = ListVehicleSerializer(data=request.data)

        if vehicle_serializer.is_valid():
            vehicle_serializer.save()
            return Response(vehicle_serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("error", vehicle_serializer.errors)
            return Response(
                vehicle_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def put(self, request):
        vehicle_id = request.POST["vehicle_id"]

        vehicle = Listed_Vehicles.objects.get(id=vehicle_id)

        vehicle.delete()

        return Response(status=status.HTTP_200_OK)

    def patch(self, request):
        discount = request.data.get("discount")
        vehicle_id = request.data.get("vehicle_id")
        print("request.post", request.data)

        if discount:
            vehicle = Listed_Vehicles.objects.get(id=vehicle_id)
            vehicle.discount = discount
            vehicle.save()
            return Response(status=status.HTTP_201_CREATED)

        edited_form_data = json.loads(request.data["formData"])

        print(edited_form_data)
        exterior = request.data.get("rcBook")

        print(exterior)
        vehicle_id = request.data["vehicle_id"]

        vehicle = Listed_Vehicles.objects.get(id=vehicle_id)

        vehicle.vehicle_number = edited_form_data["vehicle_number"]
        vehicle.make = edited_form_data["make"]
        vehicle.model = edited_form_data["model"]
        vehicle.varient = edited_form_data["varient"]
        vehicle.fuel_type = edited_form_data["fuel_type"]
        vehicle.place = edited_form_data["place"]
        vehicle.price = edited_form_data["price"]
        vehicle.fuel_available = edited_form_data["fuel_available"]
        vehicle.transmission = edited_form_data["transmission"]
        vehicle.save()

        print(vehicle_id)

        return Response(status=status.HTTP_202_ACCEPTED)


class Cart_Management(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        current_user_id = request.user.id

        data = request.data["params"]

        product_id = data["product_id"]
        remove_from_cart = data["remove"]

        current_user = CustomUser.objects.get(id=current_user_id)
        new_cart_item = Listed_Vehicles.objects.get(id=product_id)

        if remove_from_cart == True:
            Cart_Items.objects.filter(
                user=current_user_id, cart_item_id=product_id
            ).delete()
            return Response(status=status.HTTP_202_ACCEPTED)

        new_cart_item = Cart_Items.objects.create(
            user=current_user, cart_item=new_cart_item
        )

        new_cart_item.save()

        return Response(status=status.HTTP_202_ACCEPTED)

    def get(self, request):
        current_user_id = request.user.id

        cart_items = list(
            Cart_Items.objects.filter(user=current_user_id).values_list(
                "cart_item", flat=True
            )
        )

        vehicles_incart = Listed_Vehicles.objects.filter(id__in=cart_items)

        vehicles_incart = ListVehicleSerializer(vehicles_incart, many=True)

        return Response(vehicles_incart.data)


@authentication_classes([JWTAuthentication])
@permission_classes((IsAuthenticated,))
@api_view(
    ["GET"],
)
def get_user_liked(request):
    current_user_id = request.user.id
    print(current_user_id)

    cart_items = Cart_Items.objects.filter(user=current_user_id).values_list(
        "cart_item", flat=True
    )

    wishlist_items = Whishlist.objects.filter(user=current_user_id).values_list(
        "wishlist_item", flat=True
    )

    response_data = {"cart_items": cart_items, "wishlist_items": wishlist_items}

    return Response(response_data)


class Wishlist_Management(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_id = request.user.id

        data = request.data["params"]

        product_id = data["product_id"]
        remove_from_wishlist = data["remove"]

        user = CustomUser.objects.get(id=user_id)

        product = Listed_Vehicles.objects.get(id=product_id)

        if remove_from_wishlist == True:
            print("remove started")
            Whishlist.objects.filter(user=user, wishlist_item=product).delete()
            return Response(status=status.HTTP_202_ACCEPTED)

        wishlist_item = Whishlist.objects.create(user=user, wishlist_item=product)

        wishlist_item.save()

        return Response(status=status.HTTP_200_OK)

    def get(self, request):
        user_id = request.user.id
        user = CustomUser.objects.get(id=user_id)

        wishlist_items = list(
            Whishlist.objects.filter(user=user).values_list("wishlist_item", flat=True)
        )

        vehicles_inwishlist = Listed_Vehicles.objects.filter(id__in=wishlist_items)

        vehicles_inwishlist = ListVehicleSerializer(vehicles_inwishlist, many=True)

        return Response(vehicles_inwishlist.data)


class Manage_orders(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        current_user_id = request.user.id

        products = request.data.get("products").split(",")
        delivery_date = request.data.get("deliveryDate")
        return_date = request.data.get("returnDate")
        days_count = int(request.data.get("days"))
        shipping_address_id = int(request.data.get("shipping_address_id"))
        gateway_payment = request.data.get("payment_method")
        coupon_discount = int(request.data.get("coupon_discount"))
        print("gateway: ", gateway_payment)

        final_amount = int(request.data.get("checkoutAmount"))

        customer = CustomUser.objects.get(id=current_user_id)

        current_dateTime = datetime.now(pytz.timezone("Asia/Kolkata"))

        delivery_date = datetime.strptime(delivery_date, "%a, %d %b %Y %H:%M:%S GMT")
        # delivery_date=datetime.strptime(delivery_date)

        return_date = datetime.strptime(return_date, "%a, %d %b %Y %H:%M:%S GMT")

        shipping_address = Address.objects.get(id=shipping_address_id)

        print("The current time in india is :", current_dateTime)
        # amount = request.data["amount"]
        client = razorpay.Client(
            auth=(env["RAZORPAY_KEY_ID"], env["RAZORPAY_KEY_SECRET"])
        )

        for product_id in products:
            print("loop", product_id)
            product_instance = Listed_Vehicles.objects.get(id=product_id)

            if product_instance.availability:
                if product_instance.discount:
                    amount = round(
                        product_instance.price
                        - ((product_instance.price * product_instance.discount) / 100)
                    )
                    amount = amount * days_count + 10
                else:
                    amount = (product_instance.price * days_count) + 10
                    # +10 shipping charge for each vehicle

                checkout_amount = amount + amount * 0.12

                product = Listed_Vehicles.objects.get(id=product_id)
                seller_id = product.owner_id
                seller = CustomUser.objects.get(id=seller_id)

                new_order = Order_Details.objects.create(  # latest bug..payment is accepted but order not created //solved
                    product=product_id,
                    customer=customer,
                    order_date=current_dateTime,
                    deliver_date=delivery_date,
                    return_date=return_date,
                    order_status="Processing",
                    amount=checkout_amount,
                    seller=seller,
                    shipping_address=shipping_address,
                    payment_status=PaymentStatus.PENDING,  #  brrrrr here
                )
                new_order.save()

                product_instance.availability = False
                product_instance.save()
        if gateway_payment == "false":
            wallet_cash = customer.wallet_cash
            print("wallet_cash : ", wallet_cash)
            customer.wallet_cash = wallet_cash - final_amount

            customer.save()
            return Response(status=status.HTTP_201_CREATED)
        data = {
            "amount": int(final_amount) * 100,
            "currency": "INR",
            "payment_capture": "1",
        }
        payment = client.order.create(data=data)
        data = {"payment": payment}
        return Response(data)

    def get(self, request):
        seller_specific = request.GET.get("seller_specific")
        sales_report_period = request.GET.get("sales_report_period")

        current_user_id = request.user.id

        current_user = CustomUser.objects.get(id=current_user_id)

        if seller_specific:
            orders = Order_Details.objects.filter(seller_id=current_user.id)
        elif sales_report_period:
            year_start = f"{sales_report_period}-01-01"
            year_end = f"{sales_report_period}-12-31"
            orders = Order_Details.objects.filter(
                order_date__range=[year_start, year_end]
            )

            # successfull orders per month
            successfull_orders_yearly = orders.filter(order_status="Delivered")

            successfull_orders_by_month = (
                successfull_orders_yearly.annotate(
                    order_month=ExtractMonth("order_date")
                )
                .values("order_month")
                .annotate(order_count=Count("id"))
            )

            successfull_orders_by_month_count = [0] * 12
            for successfull_orders in successfull_orders_by_month:
                successfull_orders_by_month_count[
                    successfull_orders["order_month"] - 1
                ] = successfull_orders["order_count"]

            print(
                "successfull_orders_by_month_count", successfull_orders_by_month_count
            )

            # Cancelled Orders per Month

            cancelled_orders_yearly = orders.filter(order_status="Cancelled")

            cancelled_orders_by_month = (
                cancelled_orders_yearly.annotate(order_month=ExtractMonth("order_date"))
                .values("order_month")
                .annotate(order_count=Count("id"))
            )

            cancelled_orders_by_month_count = [0] * 12
            for cancelled_orders in cancelled_orders_by_month:
                cancelled_orders_by_month_count[
                    cancelled_orders["order_month"] - 1
                ] = cancelled_orders["order_count"]

            print("cancelled_orders_by_month_count", cancelled_orders_by_month_count)

            response = {
                "successfull_orders": successfull_orders_by_month_count,
                "cancelled_orders": cancelled_orders_by_month_count,
            }
            return Response(response)

        else:
            orders = Order_Details.objects.filter(customer=current_user)

        product_id = orders.values_list("product", flat=True)
        order_status = orders.values_list("order_status", flat=True)
        orders = OrderSerializer(orders, many=True)

        products = []
        for id in product_id:
            query_set = Listed_Vehicles.objects.filter(id=id)

            products.extend(query_set)

        products = ListVehicleSerializer(products, many=True)

        order_status_numeric = []
        for status in order_status:
            if status == "Cancelled":
                order_status_numeric.append(0)
            if status == "Processing":
                order_status_numeric.append(25)
            elif status == "Shipping":
                order_status_numeric.append(50)
            elif status == "Delivered":
                order_status_numeric.append(100)

        print(order_status_numeric)
        response_data = {
            "orders": orders.data,
            "products": products.data,
            "order_status": order_status_numeric,
        }
        return Response(response_data)

    def put(self, request):
        order_id = request.data["order_id"]

        order = Order_Details.objects.get(id=order_id)

        product_id = order.product

        order.order_status = "Cancelled"
        order.save()
        product = Listed_Vehicles.objects.get(id=product_id)
        product.availability = True
        product.save()

        customer = CustomUser.objects.get(id=request.user.id)

        customer.wallet_cash += order.amount

        customer.save()
        print(order_id)

        return Response(status=status.HTTP_200_OK)

    def patch(self, request):
        params = request.data["params"]
        order_id = params["order_id"]
        progress_status = params["progress"]

        order = Order_Details.objects.get(id=order_id)
        order.order_status = progress_status
        order.save()

        return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def handle_payment_success(request):
    # request.data is coming from frontend
    res = json.loads(request.data["response"])

    """res will be:
    {'razorpay_payment_id': 'pay_G3NivgSZLx7I9e',
    'razorpay_order_id': 'order_G3NhfSWWh5UfjQ',
    'razorpay_signature': '76b2accbefde6cd2392b5fbf098ebcbd4cb4ef8b78d62aa5cce553b2014993c0'}
    this will come from frontend which we will use to validate and confirm the payment
    """
    print("res", res)
    ord_id = ""
    raz_pay_id = ""
    raz_signature = ""

    # res.keys() will give us list of keys in res
    for key in res.keys():
        if key == "razorpay_order_id":
            ord_id = res[key]
        elif key == "razorpay_payment_id":
            raz_pay_id = res[key]
        elif key == "razorpay_signature":
            raz_signature = res[key]

    # get order by payment_id which we've created earlier with isPaid=False
    # order = Order.objects.get(order_payment_id=ord_id)

    # we will pass this whole data in razorpay client to verify the payment
    data = {
        "razorpay_order_id": ord_id,
        "razorpay_payment_id": raz_pay_id,
        "razorpay_signature": raz_signature,
    }

    client = razorpay.Client(auth=(env("RAZORPAY_KEY_ID"), env("RAZORPAY_KEY_SECRET")))

    # checking if the transaction is valid or not by passing above data dictionary in
    # razorpay client if it is "valid" then check will return None
    check = client.utility.verify_payment_signature(data)

    if check is not None:
        print("Redirect to error url or error page")
        return Response({"error": "Something went wrong"})

    # if payment is successful that means check is None then we will turn isPaid=True
    # order.isPaid = True
    # order.save()

    res_data = {"message": "payment successfully received!"}

    return Response(res_data)


class Manage_Coupons(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data["params"]
        min_price = data["min_price"]
        coupon_discount = data["coupon_discount"]
        coupon_code = data["coupon_code"]
        new_coupon = Coupon.objects.create(
            min_price=min_price,
            coupon_discount=coupon_discount,
            coupon_code=coupon_code,
        )
        new_coupon.save()

        return Response(status=status.HTTP_201_CREATED)

    def get(self, request):
        coupon_code = request.GET.get("coupon_code")
        price = int(request.GET.get("price"))

        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code)

            if coupon:
                if price >= coupon.min_price:
                    res_data = {"coupon_discount": coupon.coupon_discount}
                    return Response(res_data, status=status.HTTP_200_OK)
                res_data = {"min_price": coupon.min_price}
                return Response(res_data, status=status.HTTP_411_LENGTH_REQUIRED)
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        except Coupon.DoesNotExist:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


class Vehicle_Rating(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data["params"]
        vehicle_id = data["ratingVehicle"]
        rating = data["starValue"]
        comment = data["reviewTxt"]
        if rating is not None:
            rating = int(rating)

        user_id = request.user.id
        user = CustomUser.objects.get(id=user_id)
        vehicle = Listed_Vehicles.objects.get(id=vehicle_id)

        username = user.first_name + " " + user.last_name

        new_rating = VehicleRating.objects.create(
            user=user,
            username=username,
            vehicle=vehicle,
            rating=rating,
            comment=comment,
        )
        new_rating.save()

        return Response(status=status.HTTP_200_OK)

    def get(self, request):
        vehicle_id = request.GET.get("vehicle_id")

        vehicle = Listed_Vehicles.objects.get(id=vehicle_id)

        ratings = VehicleRating.objects.filter(vehicle=vehicle)

        ratings = Review_serializer(ratings, many=True)

        if ratings:
            response_data = {"reviews": ratings.data, "status": status.HTTP_200_OK}

            return Response(response_data)

        response_data = {"status": status.HTTP_204_NO_CONTENT}
        return Response(response_data)
