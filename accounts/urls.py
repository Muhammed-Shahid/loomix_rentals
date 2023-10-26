from django.urls import path
from . import views

urlpatterns = [
    path("current_user/", views.current_user_basic, name="current_user"),
    path(
        "current_user_all_details/",
        views.current_user_full_details,
        name="current_user_full",
    ),
    path("create_user/", views.create_user, name="create_user"),
    path("manage_address/", views.Address_View.as_view(), name="manage_address"),
    path("get_otp/", views.get_verification_otp, name="get_otp"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("edit_user/", views.edit_user, name="edit_user"),
]
