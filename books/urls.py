from rest_framework.routers import DefaultRouter
from books.views import BookViewSet, CategoryViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='books')
router.register(r'categories', CategoryViewSet, basename='categories')

urlpatterns = router.urls
