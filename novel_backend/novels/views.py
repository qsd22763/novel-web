from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

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
    ordering_fields = ['updated_at', 'view_count', 'created_at', 'word_count']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return NovelDetailSerializer
        return NovelListSerializer

    @action(detail=True, methods=['get'])
    def chapters(self, request, pk=None):
        novel = self.get_object()
        chapters = novel.chapters.all()
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


class ChapterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        novel = instance.novel
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
