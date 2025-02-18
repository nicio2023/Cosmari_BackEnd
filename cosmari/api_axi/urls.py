from django.urls import path
from .views import get_api_token, get_vehicle_plates, get_vehicle_details, get_my_vehicles_info, get_vehicle_details_with_delay



urlpatterns = [
    path('token/', get_api_token, name='token'),
    path('plates/', get_vehicle_plates, name='get_vehicle_plates'),
    path('vehicle/', get_vehicle_details, name='get_vehicle_details'),
    path('vehicles/', get_my_vehicles_info, name='get_my_vehicles_info'),
    path('vehicle_delay/', get_vehicle_details_with_delay, name='get_vehicle_details_with_delay'),
     
]





