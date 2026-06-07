from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, F, Count, Avg

from .models import Novel, Chapter
from .serializers import (
    NovelListSerializer,
    NovelDetailSerializer,
    ChapterSerializer,
    ChapterDetailSerializer
)


class NovelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Novel.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author']
    ordering_fields = ['updated_at', 'view_count', 'created_at', 'word_count', 'recommend']

    def get_queryset(self):
        queryset = Novel.objects.filter(audit_status=2).exclude(status=2)
        category = self.request.query_params.get('category')
        status = self.request.query_params.get('status')
        word_count_min = self.request.query_params.get('word_count_min')
        word_count_max = self.request.query_params.get('word_count_max')
        search = self.request.query_params.get('search')

        if category:
            queryset = queryset.filter(category=category)
        if status is not None:
            queryset = queryset.filter(status=int(status))
        if word_count_min:
            queryset = queryset.filter(word_count__gte=int(word_count_min))
        if word_count_max:
            queryset = queryset.filter(word_count__lte=int(word_count_max))
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(author__icontains=search))

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NovelDetailSerializer
        return NovelListSerializer

    def retrieve(self, request, *args, **kwargs):
        """详情接口：使用 annotate 预计算统计字段，避免序列化器 N+1 查询"""
        instance = self.get_object()
        # 用 annotate 一次性算出 chapter_count / comment_count / avg_rating
        novel = Novel.objects.filter(pk=instance.pk).annotate(
            chapter_count=Count('chapters'),
            comment_count=Count('comments'),
            avg_rating=Avg('comments__rating', filter=Q(comments__rating__gt=0)),
        ).first()
        serializer = self.get_serializer(novel)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def chapters(self, request, pk=None):
        novel = self.get_object()
        chapters = novel.chapters.filter(publish_status=1)
        serializer = ChapterSerializer(chapters, many=True)
        return Response({
            'novel_id': novel.id,
            'novel_title': novel.title,
            'chapter_count': chapters.count(),
            'chapters': serializer.data
        })

    @action(detail=False, methods=['get'])
    def search(self, request):
        q = request.query_params.get('q', '')
        novels = self.queryset.filter(
            Q(title__icontains=q) | Q(author__icontains=q)
        )
        page = self.paginate_queryset(novels)
        if page is not None:
            serializer = NovelListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = NovelListSerializer(novels, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recommend(self, request):
        limit = int(request.query_params.get('limit', 10))
        novels = self.queryset.order_by('-view_count')[:limit]
        serializer = NovelListSerializer(novels, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def category_stats(self, request):
        categories = ['玄幻', '都市', '穿越', '科幻', '游戏', '悬疑', '武侠', '历史']
        stats = {}
        for cat in categories:
            stats[cat] = Novel.objects.filter(category=cat).count()
        return Response(stats)


class ChapterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        novel = instance.novel
        Novel.objects.filter(id=novel.id).update(view_count=F('view_count') + 1)
        chapters = list(novel.chapters.order_by('chapter_order'))
        current_index = chapters.index(instance)

        prev_chapter = chapters[current_index - 1] if current_index > 0 else None
        next_chapter = chapters[current_index + 1] if current_index < len(chapters) - 1 else None

        serializer = self.get_serializer(instance)
        data = serializer.data
        data['novel_title'] = novel.title
        data['prev_chapter'] = {
            'id': prev_chapter.id,
            'title': prev_chapter.title
        } if prev_chapter else None
        data['next_chapter'] = {
            'id': next_chapter.id,
            'title': next_chapter.title
        } if next_chapter else None

        return Response(data)
