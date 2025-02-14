from django.urls import path
from .views import get_index



urlpatterns = [
    path('index/', get_index, name='search_index'),
    
    
]