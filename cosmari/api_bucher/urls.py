from django.urls import path

from .views import (get_api_token, get_assets_tracking, get_mission_data)

urlpatterns = [
    path('token-bucher/', get_api_token, name='token-bucher'),
    path('mission/', get_mission_data, name='mission'),
    path('assets-tracking/', get_assets_tracking, name="assets")
]