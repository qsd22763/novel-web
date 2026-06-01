from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout

from .models import User, Favorite, ReadingProgress, Bookmark
from .user_serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    FavoriteSerializer,
    ReadingProgressSerializer,
    BookmarkSerializer
)


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response({
                'message': '注册成功',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                'message': '登录成功',
                'user': UserSerializer(user).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'message': '退出登录成功'})

    @action(detail=False, methods=['get'])
    def me(self, request):
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        return Response({'message': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        if not request.user.is_authenticated:
            return Response({'message': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)

        user = request.user
        data = request.data

        if 'avatar' in data:
            user.avatar = data['avatar']
        if 'phone' in data:
            user.phone = data['phone']
        if 'email' in data:
            user.email = data['email']

        user.save()
        return Response({
            'message': '更新成功',
            'user': UserSerializer(user).data
        })

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        if not request.user.is_authenticated:
            return Response({'message': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)

        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({'old_password': ['请输入旧密码'], 'new_password': ['请输入新密码']}, status=400)

        if len(new_password) < 6:
            return Response({'new_password': ['密码至少6位']}, status=400)

        user = request.user
        if not user.check_password(old_password):
            return Response({'old_password': ['旧密码不正确']}, status=400)

        user.set_password(new_password)
        user.save()

        from django.contrib.auth import update_session_auth_hash
        update_session_authhash(request, user)

        return Response({'message': '密码修改成功'})


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        novel_id = request.data.get('novel')
        if Favorite.objects.filter(user=request.user, novel_id=novel_id).exists():
            return Response({'message': '已收藏'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def check(self, request):
        novel_id = request.query_params.get('novel_id')
        is_favorited = Favorite.objects.filter(user=request.user, novel_id=novel_id).exists()
        return Response({'is_favorited': is_favorited})

    @action(detail=False, methods=['post'])
    def delete_by_novel(self, request):
        novel_id = request.data.get('novel_id')
        try:
            favorite = Favorite.objects.get(user=request.user, novel_id=novel_id)
            favorite.delete()
            return Response({'message': '取消收藏成功'})
        except Favorite.DoesNotExist:
            return Response({'message': '收藏记录不存在'}, status=status.HTTP_404_NOT_FOUND)


class ReadingProgressViewSet(viewsets.ModelViewSet):
    serializer_class = ReadingProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReadingProgress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def get_progress(self, request):
        novel_id = request.query_params.get('novel_id')
        try:
            progress = ReadingProgress.objects.get(user=request.user, novel_id=novel_id)
            return Response(ReadingProgressSerializer(progress).data)
        except ReadingProgress.DoesNotExist:
            return Response({'message': '暂无阅读进度'})

    @action(detail=False, methods=['post'])
    def update_progress(self, request):
        novel_id = request.data.get('novel_id')
        chapter_id = request.data.get('chapter_id')
        position = request.data.get('position', 0)

        progress, created = ReadingProgress.objects.update_or_create(
            user=request.user,
            novel_id=novel_id,
            defaults={'chapter_id': chapter_id, 'position': position}
        )
        return Response({
            'message': '更新成功',
            'progress': ReadingProgressSerializer(progress).data
        })


class BookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def by_chapter(self, request):
        chapter_id = request.query_params.get('chapter_id')
        bookmark = Bookmark.objects.filter(user=request.user, chapter_id=chapter_id).first()
        if bookmark:
            return Response(BookmarkSerializer(bookmark).data)
        return Response({'message': '暂无书签'}, status=status.HTTP_404_NOT_FOUND)
