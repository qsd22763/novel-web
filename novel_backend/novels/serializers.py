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
    class Meta:
        model = Novel
        fields = ['id', 'title', 'author', 'cover', 'category', 'status', 'word_count', 'view_count', 'updated_at']


class NovelDetailSerializer(serializers.ModelSerializer):
    chapter_count = serializers.SerializerMethodField()

    class Meta:
        model = Novel
        fields = ['id', 'title', 'author', 'cover', 'description', 'category', 'status', 'word_count', 'view_count', 'chapter_count', 'created_at', 'updated_at']

    def get_chapter_count(self, obj):
        return obj.chapters.count()
