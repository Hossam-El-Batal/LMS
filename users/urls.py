from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterViewSet, LoginViewSet, LogoutViewSet, PasswordResetViewSet, PasswordResetConfirmViewSet

router = DefaultRouter()
router.register(r'register', RegisterViewSet, basename='register')
router.register(r'login', LoginViewSet, basename='login')
router.register(r'logout', LogoutViewSet, basename='logout')
router.register(r'password-reset', PasswordResetViewSet, basename='password-reset')
router.register(r'password-reset-confirm', PasswordResetConfirmViewSet, basename='password-reset-confirm')

urlpatterns = [
    path('', include(router.urls)),
]