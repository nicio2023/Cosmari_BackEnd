from django.http import JsonResponse
from django.shortcuts import render
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
            response.set_cookie(
                key="access_token",
                value=access_token,
                max_age=6 * 60 * 60,
                httponly=True,
                secure=True,
                samesite="Lax",
                domain="localhost",
                path="/"
            )
            response.set_cookie(
                key="refresh_token",
                max_age=6 * 60 * 60,
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite="Lax",
                domain="localhost",
                path="/"
            )
            return response
        return JsonResponse({"error": "Invalid credentials"}, status=401)

class LogoutView(APIView):
    """Endpoint per il logout """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = JsonResponse({"message": "Logged out successfully"})
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response

class RefreshTokenView(APIView):
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
                httponly=True,
                secure=True,
                samesite="Lax"
            )
            return response
        except Exception:
            return JsonResponse({"error": "Invalid refresh token"}, status=400)

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
    