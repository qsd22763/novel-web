from rest_framework.routers import DefaultRouter
from .views import NovelViewSet, ChapterViewSet
from .user_views import AuthViewSet, FavoriteViewSet, ReadingProgressViewSet, BookmarkViewSet
from .author_views import AuthorNovelViewSet, AuthorChapterViewSet
from .comment_views import CommentViewSet

router = DefaultRouter()
router.register(r'novels', NovelViewSet, basename='novel')
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'reading-progress', ReadingProgressViewSet, basename='reading-progress')
router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'author/novels', AuthorNovelViewSet, basename='author-novel')
router.register(r'author/chapters', AuthorChapterViewSet, basename='author-chapter')

urlpatterns = router.urls
