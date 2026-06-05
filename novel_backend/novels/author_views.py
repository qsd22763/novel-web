from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.conf import settings
import os
import uuid

from .models import Novel, Chapter
from .author_serializers import (
    AuthorNovelSerializer,
    AuthorNovelDetailSerializer,
    AuthorChapterSerializer,
    AuthorChapterDetailSerializer,
)


class AuthorNovelViewSet(viewsets.ModelViewSet):
    """作者作品管理接口：仅返回当前登录用户作为作者的作品"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated_at', 'created_at', 'view_count']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return AuthorNovelDetailSerializer
        return AuthorNovelSerializer

    def get_queryset(self):
        return Novel.objects.filter(author_user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_author:
            user.is_author = True
            if not user.pen_name:
                user.pen_name = user.username
            user.save(update_fields=['is_author', 'pen_name'])
        author_name = user.pen_name or user.username
        serializer.save(author_user=user, author=author_name, audit_status=1)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        total_works = qs.count()
        total_words = qs.aggregate(s=Sum('word_count'))['s'] or 0
        total_views = qs.aggregate(s=Sum('view_count'))['s'] or 0
        total_chapters = Chapter.objects.filter(novel__author_user=request.user).count()
        return Response({
            'total_works': total_works,
            'total_chapters': total_chapters,
            'total_words': total_words,
            'total_views': total_views,
        })

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        novel = self.get_object()
        novel.audit_status = 2
        novel.save(update_fields=['audit_status'])
        return Response({'message': '作品已发布', 'audit_status': novel.audit_status})

    @action(detail=True, methods=['post'])
    def take_down(self, request, pk=None):
        novel = self.get_object()
        novel.status = 2
        novel.save(update_fields=['status'])
        return Response({'message': '作品已下架', 'status': novel.status})

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_cover(self, request):
        f = request.FILES.get('file')
        if not f:
            return Response({'detail': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        ext = os.path.splitext(f.name)[1].lower() or '.jpg'
        if ext not in {'.jpg', '.jpeg', '.png', '.webp', '.gif'}:
            return Response({'detail': '仅支持 jpg/png/webp/gif'}, status=status.HTTP_400_BAD_REQUEST)
        if f.size > 5 * 1024 * 1024:
            return Response({'detail': '文件不能超过 5MB'}, status=status.HTTP_400_BAD_REQUEST)
        sub_dir = os.path.join(settings.MEDIA_ROOT, 'covers')
        os.makedirs(sub_dir, exist_ok=True)
        filename = f'{uuid.uuid4().hex}{ext}'
        full_path = os.path.join(sub_dir, filename)
        with open(full_path, 'wb') as out:
            for chunk in f.chunks():
                out.write(chunk)
        url = f'{settings.MEDIA_URL}covers/{filename}'
        return Response({'url': url})


class AuthorChapterViewSet(viewsets.ModelViewSet):
    """作者章节管理：仅允许操作当前用户所属作品的章节"""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list']:
            return AuthorChapterSerializer
        return AuthorChapterDetailSerializer

    def get_queryset(self):
        qs = Chapter.objects.filter(novel__author_user=self.request.user)
        novel_id = self.request.query_params.get('novel')
        if novel_id:
            qs = qs.filter(novel_id=novel_id)
        return qs.order_by('chapter_order')

    def perform_create(self, serializer):
        novel_id = self.request.data.get('novel')
        novel = get_object_or_404(Novel, pk=novel_id, author_user=self.request.user)
        last = novel.chapters.order_by('-chapter_order').first()
        next_order = (last.chapter_order + 1) if last else 1
        content = self.request.data.get('content', '') or ''
        word_count = len(content.replace(' ', '').replace('\n', ''))
        chapter = serializer.save(
            novel=novel,
            chapter_order=self.request.data.get('chapter_order') or next_order,
            word_count=word_count,
        )
        novel.word_count = (novel.chapters.aggregate(s=Sum('word_count'))['s'] or 0)
        novel.save(update_fields=['word_count', 'updated_at'])
        return chapter

    def perform_update(self, serializer):
        instance = serializer.instance
        content = self.request.data.get('content', instance.content) or ''
        word_count = len(content.replace(' ', '').replace('\n', ''))
        chapter = serializer.save(word_count=word_count)
        novel = chapter.novel
        novel.word_count = (novel.chapters.aggregate(s=Sum('word_count'))['s'] or 0)
        novel.save(update_fields=['word_count', 'updated_at'])
        return chapter

    def perform_destroy(self, instance):
        novel = instance.novel
        instance.delete()
        novel.word_count = (novel.chapters.aggregate(s=Sum('word_count'))['s'] or 0)
        novel.save(update_fields=['word_count', 'updated_at'])

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        chapter = self.get_object()
        chapter.publish_status = 1
        chapter.save(update_fields=['publish_status', 'updated_at'])
        return Response({'message': '章节已发布', 'publish_status': chapter.publish_status})
