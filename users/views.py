from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import User
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    PasswordResetConfirmSerializer,
)


class RegisterViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(methods=['post'], detail=False)
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'User registered successfully',
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_201_CREATED)


class LoginViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(methods=['post'], detail=False)
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = validated_data['user']

        response = Response(status=status.HTTP_200_OK)
        response.set_cookie(
            key='access_token',
            value=validated_data['access_token'],
            httponly=True,
            secure=True,
            samesite=None,
        )
        response.set_cookie(
            key='refresh_token',
            value=validated_data['refresh_token'],
            httponly=True,
            secure=True,
            samesite=None,
        )
        response.data = {"message": "Login successful", "user": user.id, "access_token": validated_data['access_token']}

        return response


class LogoutViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(methods=['post'], detail=False)
    def logout(self, request):
        # Delete the tokens from cookies
        response = Response({
            "message": "Logged out successfully"
        }, status=status.HTTP_205_RESET_CONTENT)

        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response


class PasswordResetViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(methods=['post'], detail=False)
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.send_reset_link()
        return Response(result, status=status.HTTP_200_OK)


class PasswordResetConfirmViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(methods=['post'], detail=False)
    def reset_password_confirm(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
