from rest_framework import serializers
from django.db.models import Count, Avg
from .models import Novel, Chapter


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'chapter_order', 'word_count', 'created_at']


class ChapterDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['id', 'novel_id', 'title', 'content', 'chapter_order', 'word_count', 'created_at']


class NovelListSerializer(serializers.ModelSerializer):
    latest_chapter = serializers.SerializerMethodField()

    class Meta:
        model = Novel
        fields = [
            'id', 'title', 'author', 'cover', 'description', 'category',
            'status', 'word_count', 'view_count', 'updated_at',
            'latest_chapter',
            'is_adapted', 'is_recommended', 'recommend_comment', 'topic_tag',
        ]

    def get_latest_chapter(self, obj):
        latest = obj.chapters.order_by('-chapter_order').first()
        return latest.title if latest else None


class NovelDetailSerializer(serializers.ModelSerializer):
    """小说详情序列化器 — 使用 annotate 预计算统计字段，避免 N+1 查询"""
    chapter_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    avg_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Novel
        fields = [
            'id', 'title', 'author', 'cover', 'description', 'category',
            'status', 'word_count', 'view_count',
            'chapter_count', 'comment_count', 'avg_rating',
            'created_at', 'updated_at'
        ]
