from django.urls import path
from . import views
urlpatterns = [
      path('all_users/', views.get_all_users, name ='all_users'),
      path('all_vehicles/', views.get_all_vehicles, name ='all_vehicles'),
      path('manage_vehicles/', views.manage_vehicles, name ='manage_vehicles'),
      path('manage_user/', views.manage_user, name ='manage_user'),
      path('view_coupons/', views.view_coupons, name ='view_coupons'),

      
      ]
      