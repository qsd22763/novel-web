from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Comment, Novel
from .comment_serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Comment.objects.select_related('user', 'novel').all()
        novel_id = self.request.query_params.get('novel')
        if novel_id:
            qs = qs.filter(novel_id=novel_id)
        return qs

    def perform_create(self, serializer):
        novel_id = self.request.data.get('novel')
        novel = Novel.objects.get(pk=novel_id)
        serializer.save(user=self.request.user, novel=novel)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user_id != request.user.id:
            return Response({'detail': '无权删除他人评论'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        novel_id = request.query_params.get('novel')
        if not novel_id:
            return Response({'detail': '缺少 novel 参数'}, status=400)
        qs = Comment.objects.filter(novel_id=novel_id, rating__gt=0)
        count = qs.count()
        avg = round(sum(qs.values_list('rating', flat=True)) / count, 1) if count else 0
        return Response({
            'comment_count': Comment.objects.filter(novel_id=novel_id).count(),
            'rating_count': count,
            'avg_rating': avg,
        })
