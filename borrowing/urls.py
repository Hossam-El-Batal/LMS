
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BorrowingViewSet, BorrowedItemViewSet

router = DefaultRouter()
router.register(r'borrowings', BorrowingViewSet, basename='borrowings')
router.register(r'items', BorrowedItemViewSet, basename='borrowed-items')

urlpatterns = [
    path('', include(router.urls)),
]