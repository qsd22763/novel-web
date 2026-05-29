from rest_framework import serializers
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
        fields = ['id', 'title', 'author', 'cover', 'description', 'category', 'status', 'word_count', 'view_count', 'updated_at', 'latest_chapter']

    def get_latest_chapter(self, obj):
        latest = obj.chapters.order_by('-chapter_order').first()
        return latest.title if latest else None


class NovelDetailSerializer(serializers.ModelSerializer):
    chapter_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Novel
        fields = ['id', 'title', 'author', 'cover', 'description', 'category', 'status', 'word_count', 'view_count', 'chapter_count', 'comment_count', 'avg_rating', 'created_at', 'updated_at']

    def get_chapter_count(self, obj):
        return obj.chapters.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_avg_rating(self, obj):
        rated = obj.comments.filter(rating__gt=0)
        count = rated.count()
        if not count:
            return 0
        total = sum(rated.values_list('rating', flat=True))
        return round(total / count, 1)
