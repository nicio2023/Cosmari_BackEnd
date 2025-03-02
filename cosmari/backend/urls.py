from django.urls import path
from .views import get_users, create_user, LoginView, RegisterView, LogoutView, RefreshTokenView
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="API JWT Authentication",
        default_version='v1',
        description="Documentazione delle API di autenticazione con JWT",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('users/', get_users, name='get_users'),
    path('users/create/', create_user, name='create_user'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui')
]