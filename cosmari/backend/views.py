from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework import status
from .models import User
from .serializer import UserSerializer
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import  TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken
User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """Endpoint per la registrazione di un nuovo utente"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    """Endpoint per l'autenticazione e il rilascio del token JWT"""
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            response = JsonResponse({"message": "Login successful"})
            print(access_token)
            response.set_cookie(
                key="access_token",
                value=access_token,
                expires= settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                expires=settings.SIMPLE_JWT['SLIDING_TOKEN_REFRESH_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            return response
        return JsonResponse({"error": "Invalid credentials"}, status=401)

class LogoutView(APIView):
    """Endpoint per il logout """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                refresh.blacklist()
            except Exception as e:
                return Response({"errore": "Token non inserito nella blacklist!!"+ str(e)}, status=500)
        response = JsonResponse({"message": "Logged out successfully"}, status=200)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class RefreshTokenView(TokenRefreshView):
    """Endpoint per rinnovare il token di accesso usando il refresh token salvato nel cookie"""
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return JsonResponse({"error": "No refresh token found"}, status=400)
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            response = JsonResponse({"message": "Token refreshed"})
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )
            return response
        except InvalidToken :
            return JsonResponse({"error": "Invalid token"}, status=401)

@api_view(['GET'])
def get_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True);
    return Response(serializer.data)

@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status = status.HTTP_201_CREATED)
    