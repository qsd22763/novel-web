from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, F, Count, Avg, IntegerField, Max
from django.db.models.functions import Coalesce

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

    @action(detail=False, methods=['get'])
    def home_data(self, request):
        """首页聚合数据：一次性返回12个分区，减少前端请求次数"""
        base_qs = Novel.objects.filter(audit_status=2).exclude(status=2)
        s = NovelListSerializer

        # 1. 轮播Banner（推荐/高阅读量书籍，取5本）
        banner = list(base_qs.order_by('-view_count')[:5])

        # 2. 四大榜单（各TOP10）
        # 女频分类：穿越/悬疑/都市/历史；男频分类：玄幻/武侠/科幻/游戏
        FEMALE_CATS = ['穿越', '悬疑', '都市', '历史']
        MALE_CATS = ['玄幻', '武侠', '科幻', '游戏']

        hot_female = list(base_qs.filter(category__in=FEMALE_CATS)
                          .annotate(hot_score=Coalesce('view_count', 0, output_field=IntegerField()) +
                                     Coalesce('recommend', 0, output_field=IntegerField()))
                          .order_by('-hot_score')[:10])
        hot_male = list(base_qs.filter(category__in=MALE_CATS)
                        .annotate(hot_score=Coalesce('view_count', 0, output_field=IntegerField()) +
                                   Coalesce('recommend', 0, output_field=IntegerField()))
                        .order_by('-hot_score')[:10])
        new_female = list(base_qs.filter(category__in=FEMALE_CATS)
                         .order_by('-created_at')[:10])
        new_male = list(base_qs.filter(category__in=MALE_CATS)
                       .order_by('-created_at')[:10])

        # 3. 男女频专题
        female_topic = list(base_qs.filter(topic_tag='女频专题').order_by('-view_count')[:15])
        male_topic = list(base_qs.filter(topic_tag='男频专题').order_by('-view_count')[:15])

        # 4. 影视改编专区
        adapted = list(base_qs.filter(is_adapted=True).order_by('-view_count')[:10])

        # 5. 总编推荐
        recommended = list(base_qs.filter(is_recommended=True).order_by('-updated_at')[:3])

        # 6. 四大分类快捷栏
        quick_cats = ['穿越', '玄幻', '都市', '武侠']
        quick_cat_data = {}
        for cat in quick_cats:
            quick_cat_data[cat] = s(list(base_qs.filter(category=cat).order_by('-view_count')[:4]), many=True).data

        # 7. 签约新书（近期审核通过）
        signed_new = list(base_qs.order_by('-created_at')[:18])

        # 8. 最近更新（按章节更新时间倒序）
        recent_updated = list(
            base_qs.annotate(last_chapter_time=Max('chapters__created_at'))
            .exclude(last_chapter_time=None)
            .order_by('-last_chapter_time')[:20]
        )

        # 9. 完结榜单
        finished_female = list(base_qs.filter(status=1, category__in=FEMALE_CATS)
                               .order_by('-view_count')[:10])
        finished_male = list(base_qs.filter(status=1, category__in=MALE_CATS)
                             .order_by('-view_count')[:10])

        return Response({
            'banner': s(banner, many=True).data,
            'rankings': {
                'hot_female': s(hot_female, many=True).data,
                'hot_male': s(hot_male, many=True).data,
                'new_female': s(new_female, many=True).data,
                'new_male': s(new_male, many=True).data,
            },
            'topics': {
                'female': s(female_topic, many=True).data,
                'male': s(male_topic, many=True).data,
            },
            'adapted': s(adapted, many=True).data,
            'recommended': s(recommended, many=True).data,
            'quick_categories': quick_cat_data,
            'signed_new': s(signed_new, many=True).data,
            'recent_updated': s(recent_updated, many=True).data,
            'finished': {
                'female': s(finished_female, many=True).data,
                'male': s(finished_male, many=True).data,
            },
        })


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
