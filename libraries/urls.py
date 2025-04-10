from rest_framework.routers import DefaultRouter
from libraries.views import LibraryViewSet, BookCopyViewSet
router = DefaultRouter()

router.register(r'libraries', LibraryViewSet, basename='libraries')
router.register(r'copies', BookCopyViewSet, basename='copies')


urlpatterns = router.urls
