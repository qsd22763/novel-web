from rest_framework import serializers
from .models import Novel, Chapter


class AuthorNovelSerializer(serializers.ModelSerializer):
    chapter_count = serializers.SerializerMethodField()
    audit_status_display = serializers.CharField(source='get_audit_status_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Novel
        fields = [
            'id', 'title', 'author', 'cover', 'description', 'category', 'tags',
            'status', 'status_display', 'audit_status', 'audit_status_display',
            'word_count', 'view_count', 'chapter_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['author', 'word_count', 'view_count', 'created_at', 'updated_at']

    def get_chapter_count(self, obj):
        return obj.chapters.count()


class AuthorNovelDetailSerializer(AuthorNovelSerializer):
    class Meta(AuthorNovelSerializer.Meta):
        fields = AuthorNovelSerializer.Meta.fields


class AuthorChapterSerializer(serializers.ModelSerializer):
    publish_status_display = serializers.CharField(source='get_publish_status_display', read_only=True)

    class Meta:
        model = Chapter
        fields = [
            'id', 'novel', 'title', 'chapter_order', 'word_count',
            'publish_status', 'publish_status_display',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['word_count', 'created_at', 'updated_at']


class AuthorChapterDetailSerializer(serializers.ModelSerializer):
    publish_status_display = serializers.CharField(source='get_publish_status_display', read_only=True)

    class Meta:
        model = Chapter
        fields = [
            'id', 'novel', 'title', 'content', 'chapter_order', 'word_count',
            'publish_status', 'publish_status_display',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['word_count', 'created_at', 'updated_at']
