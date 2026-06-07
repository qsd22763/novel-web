# -*- coding: utf-8 -*-
"""关注作者 - 用户端接口"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .models import User, UserFollow, Novel


class FollowSerializer(object):
    """关注序列化"""
    @staticmethod
    def serialize_follow(follow):
        return {
            'id': follow.id,
            'author_name': follow.author_name,
            'created_at': follow.created_at.strftime('%Y-%m-%d %H:%M:%S') if follow.created_at else '',
        }

    @staticmethod
    def serialize_author_info(author_name):
        """作者信息（含小说数、粉丝数）"""
        novels = Novel.objects.filter(author=author_name, audit_status=2)
        follower_count = UserFollow.objects.filter(author_name=author_name).count()
        return {
            'name': author_name,
            'novel_count': novels.count(),
            'follower_count': follower_count,
            'novels': [
                {
                    'id': n.id,
                    'title': n.title,
                    'cover': n.cover,
                    'category': n.category,
                    'status': n.status,
                    'word_count': n.word_count,
                    'updated_at': n.updated_at.strftime('%Y-%m-%d') if n.updated_at else '',
                }
                for n in novels[:20]
            ],
        }


class FollowPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class FollowViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # ── 1. 关注作者 ──
    @action(detail=False, methods=['post'])
    def follow(self, request):
        author_name = request.data.get('author_name', '').strip()
        if not author_name:
            return Response({'message': '作者名不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        if isinstance(request.user, (type(None),)):
            return Response({'message': '请先登录'}, status=status.HTTP_401_UNAUTHORIZED)

        obj, created = UserFollow.objects.get_or_create(
            user=request.user,
            defaults={'author_name': author_name},
        )
        if created:
            return Response({'message': '关注成功', 'followed': True})
        else:
            # 已存在则更新author_name（处理改名情况）
            return Response({'message': '已关注过该作者', 'followed': True})

    # ── 2. 取消关注 ──
    @action(detail=False, methods=['post'])
    def unfollow(self, request):
        author_name = request.data.get('author_name', '').strip()
        if not author_name:
            return Response({'message': '作者名不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = UserFollow.objects.filter(user=request.user, author_name=author_name).delete()
        if deleted:
            return Response({'message': '已取消关注', 'followed': False})
        return Response({'message': '未关注该作者', 'followed': False})

    # ── 3. 查询是否已关注某作者 ──
    @action(detail=False, methods=['get'])
    def check(self, request):
        author_name = request.query_params.get('author_name', '').strip()
        if not author_name:
            return Response({'followed': False}, status=status.HTTP_200_OK)

        followed = UserFollow.objects.filter(
            user=request.user, author_name=author_name
        ).exists()
        return Response({'followed': followed})

    # ── 4. 我的关注列表 ──
    @action(detail=False, methods=['get'])
    def my_follows(self, request):
        follows = UserFollow.objects.filter(user=request.user).select_related('user')
        paginator = FollowPagination()
        page = paginator.paginate_queryset(follows, request)
        if page is not None:
            items = [FollowSerializer.serialize_follow(f) for f in page]
            return paginator.get_paginated_response(items)
        items = [FollowSerializer.serialize_follow(f) for f in follows]
        return Response({'results': items, 'count': len(items)})

    # ── 5. 作者的粉丝列表（不传author_name则返回全部，供管理后台使用） ──
    @action(detail=False, methods=['get'])
    def followers(self, request):
        author_name = request.query_params.get('author_name', '').strip()

        qs = UserFollow.objects.all().select_related('user')
        if author_name:
            qs = qs.filter(author_name=author_name)

        paginator = FollowPagination()
        page = paginator.paginate_queryset(qs, request)
        _safe_username = lambda f: getattr(f.user, 'username', '(已注销)') if f.user else '(已注销)'
        if page is not None:
            items = [{
                'id': f.id,
                'username': _safe_username(f),
                'author_name': f.author_name,
                'created_at': f.created_at.strftime('%Y-%m-%d %H:%M:%S') if f.created_at else '',
            } for f in page]
            return paginator.get_paginated_response(items)
        items = [{
            'id': f.id,
            'username': _safe_username(f),
            'author_name': f.author_name,
            'created_at': f.created_at.strftime('%Y-%m-%d %H:%M:%S') if f.created_at else '',
        } for f in qs]
        return Response({'results': items, 'count': len(items)})

    # ── 7. 管理员删除粉丝记录 ──
    @action(detail=False, methods=['post'])
    def admin_delete(self, request):
        record_id = request.data.get('id')
        if not record_id:
            return Response({'message': '记录ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = UserFollow.objects.filter(id=record_id).delete()
        if deleted:
            return Response({'message': '已删除'})
        return Response({'message': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)

    # ── 6. 作者主页信息（作者详情+小说列表） ──
    @action(detail=False, methods=['get'])
    def author_detail(self, request):
        author_name = request.query_params.get('author_name', '').strip()
        if not author_name:
            return Response({'message': '作者名不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        info = FollowSerializer.serialize_author_info(author_name)
        # 当前用户是否已关注
        info['is_followed'] = False
        if request.user and not isinstance(request.user, type(None)) and hasattr(request.user, 'id'):
            info['is_followed'] = UserFollow.objects.filter(
                user=request.user, author_name=author_name
            ).exists()

        return Response(info)
