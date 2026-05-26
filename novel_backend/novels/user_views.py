from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout

from .models import User, Favorite, ReadingProgress
from .user_serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    LoginSerializer,
    FavoriteSerializer,
    ReadingProgressSerializer
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


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        novel_id = request.data.get('novel')
        if Favorite.objects.filter(user=request.user, novel_id=novel_id).exists():
            return Response({'message': '已收藏'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def check(self, request):
        novel_id = request.query_params.get('novel_id')
        is_favorited = Favorite.objects.filter(user=request.user, novel_id=novel_id).exists()
        return Response({'is_favorited': is_favorited})


class ReadingProgressViewSet(viewsets.ModelViewSet):
    serializer_class = ReadingProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReadingProgress.objects.filter(user=self.request.user)

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
