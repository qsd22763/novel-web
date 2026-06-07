from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import NovelViewSet, ChapterViewSet
from .user_views import AuthViewSet, FavoriteViewSet, ReadingProgressViewSet, BookmarkViewSet
from .author_views import AuthorNovelViewSet, AuthorChapterViewSet
from .comment_views import CommentViewSet
from .admin_views import AdminAdvertisementViewSet, AdminAnnouncementViewSet, AdminNovelViewSet, PublicAdvertisementViewSet, PublicAnnouncementViewSet, BookCategoryViewSet, ViolationRecordViewSet, DashboardStatsView, AdminCheckInViewSet, AdminMembershipOrderViewSet
from .checkin_views import CheckInViewSet, MembershipViewSet
from .follow_views import FollowViewSet
from .rating_views import RatingViewSet

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
router.register(r'admin/advertisements', AdminAdvertisementViewSet, basename='admin-advertisement')
router.register(r'admin/announcements', AdminAnnouncementViewSet, basename='admin-announcement')
router.register(r'admin/books', AdminNovelViewSet, basename='admin-novel')
router.register(r'public/advertisements', PublicAdvertisementViewSet, basename='public-advertisement')
router.register(r'public/announcements', PublicAnnouncementViewSet, basename='public-announcement')
router.register(r'admin/categories', BookCategoryViewSet, basename='admin-category')
router.register(r'admin/violations', ViolationRecordViewSet, basename='admin-violation')
router.register(r'checkin', CheckInViewSet, basename='checkin')
router.register(r'membership', MembershipViewSet, basename='membership')
router.register(r'admin/checkins', AdminCheckInViewSet, basename='admin-checkin')
router.register(r'admin/orders', AdminMembershipOrderViewSet, basename='admin-order')
router.register(r'follow', FollowViewSet, basename='follow')
router.register(r'rating', RatingViewSet, basename='rating')

urlpatterns = router.urls + [
    path('admin/dashboard-stats', DashboardStatsView.as_view(), name='admin-dashboard-stats'),
]
