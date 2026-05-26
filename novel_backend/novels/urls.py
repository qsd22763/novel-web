from rest_framework.routers import DefaultRouter
from .views import NovelViewSet, ChapterViewSet
from .user_views import AuthViewSet, FavoriteViewSet, ReadingProgressViewSet

router = DefaultRouter()
router.register(r'novels', NovelViewSet, basename='novel')
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'reading-progress', ReadingProgressViewSet, basename='reading-progress')

urlpatterns = router.urls
