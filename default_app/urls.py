from django.urls import path

from . import views

urlpatterns = [
    path("app_view/", views.HomeView.as_view(), name="home"),
    path("vehicles_view/", views.VehicleView.as_view(), name="vehicles_view"),
    path("manage_cart/", views.Cart_Management.as_view(), name="manage_cart"),
    path("manage_wishlist/", views.Wishlist_Management.as_view(), name="wishlist"),
    path("manage_coupons/", views.Manage_Coupons.as_view(), name="coupons"),
    path("user_liked/", views.get_user_liked, name="user_liked"),
    path("manage_order/", views.Manage_orders.as_view(), name="user_liked"),
    path("vehicle_rating/", views.Vehicle_Rating.as_view, name="vehicle_search"),
    path("payment/success/", views.handle_payment_success, name="payment_success"),
]
