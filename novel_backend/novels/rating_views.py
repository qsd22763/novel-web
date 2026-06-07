# -*- coding: utf-8 -*-
"""小说评分接口 — 提交评分 / 评分统计 / 我的评分"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count

from .models import NovelRating


class RatingViewSet(viewsets.GenericViewSet):
    """评分视图集"""
    queryset = NovelRating.objects.all()

    def get_serializer_class(self):
        from rest_framework.serializers import ModelSerializer

        class RatingSerializer(ModelSerializer):
            class Meta:
                model = NovelRating
                fields = ['id', 'novel', 'user', 'score', 'created_at']
                read_only_fields = ['id', 'user', 'created_at']

        return RatingSerializer

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def submit(self, request):
        """提交/修改评分（每个用户每本小说只能评一次，重复提交则更新）"""
        novel_id = request.data.get('novel_id')
        score = request.data.get('score')

        if not novel_id or score is None:
            return Response(
                {'message': '缺少必要参数 novel_id 或 score'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            novel_id = int(novel_id)
            score = int(score)
        except (ValueError, TypeError):
            return Response(
                {'message': '参数格式错误'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if score < 1 or score > 5:
            return Response(
                {'message': '评分必须在 1-5 之间'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 检查小说是否存在
        from .models import Novel
        if not Novel.objects.filter(id=novel_id).exists():
            return Response(
                {'message': '小说不存在'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 创建或更新评分（unique_together 保证唯一性）
        rating, created = NovelRating.objects.update_or_create(
            user=request.user,
            novel_id=novel_id,
            defaults={'score': score},
        )

        return Response({
            'id': rating.id,
            'novel_id': novel_id,
            'score': score,
            'created': created,
            'message': '评分成功' if created else '评分已更新',
        })

    @action(detail=False, methods=['get'])
    def stat(self, request):
        """获取小说评分统计：平均分 + 评分人数 + 各星占比"""
        novel_id = request.query_params.get('novel_id')
        if not novel_id:
            return Response(
                {'message': '缺少参数 novel_id'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = NovelRating.objects.filter(novel_id=novel_id)
        agg = qs.aggregate(
            avg_score=Avg('score'),
            total_count=Count('id'),
        )
        avg = float(agg['avg_score'] or 0)
        total = int(agg['total_count'] or 0)

        # 各星级人数分布
        distribution = {}
        for s in range(1, 6):
            distribution[str(s)] = qs.filter(score=s).count()

        return Response({
            'novel_id': int(novel_id),
            'avg_score': round(avg, 1),
            'total_count': total,
            'distribution': distribution,
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_rating(self, request):
        """获取当前用户对某本小说的评分（未评分返回空）"""
        novel_id = request.query_params.get('novel_id')
        if not novel_id:
            return Response({'score': None})

        try:
            rating = NovelRating.objects.get(user=request.user, novel_id=novel_id)
            return Response({'score': rating.score})
        except NovelRating.DoesNotExist:
            return Response({'score': None})
