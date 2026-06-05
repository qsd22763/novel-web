from rest_framework import serializers
from .models import Advertisement, Announcement, Novel, OperationLog, BookCategory, ViolationRecord, ChapterUploadLog, Chapter


class AdvertisementSerializer(serializers.ModelSerializer):
    ad_type_display = serializers.CharField(source='get_ad_type_display', read_only=True)
    position_display = serializers.CharField(source='get_position_display', read_only=True)

    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'ad_type', 'ad_type_display', 'image_url', 'link_url',
            'position', 'position_display', 'is_active', 'start_time', 'end_time',
            'click_count', 'view_count', 'sort_order', 'created_at', 'updated_at'
        ]


class AnnouncementSerializer(serializers.ModelSerializer):
    announcement_type_display = serializers.CharField(source='get_announcement_type_display', read_only=True)

    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'announcement_type', 'announcement_type_display',
            'is_pinned', 'is_active', 'created_at', 'updated_at'
        ]


class AdminNovelSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    audit_status_display = serializers.CharField(source='get_audit_status_display', read_only=True)
    chapter_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    author_name = serializers.CharField(source='author_user.pen_name', read_only=True, default='')

    class Meta:
        model = Novel
        fields = [
            'id', 'title', 'author', 'author_user', 'author_name', 'cover',
            'description', 'category', 'tags', 'status', 'status_display',
            'audit_status', 'audit_status_display', 'word_count', 'view_count',
            'recommend', 'chapter_count', 'comment_count', 'created_at', 'updated_at'
        ]

    def get_chapter_count(self, obj):
        return obj.chapters.count()

    def get_comment_count(self, obj):
        return obj.comments.count()


class OperationLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True, default='')

    class Meta:
        model = OperationLog
        fields = ['id', 'user', 'username', 'action', 'target_type', 'target_id',
                  'target_name', 'detail', 'ip_address', 'created_at']


class BookCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = BookCategory
        fields = ['id', 'name', 'parent', 'parent_id', 'sort_order', 'is_active',
                  'color', 'description', 'book_count', 'children', 'created_at']

    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by('sort_order', 'id')
        return BookCategorySerializer(children, many=True).data


class ViolationRecordSerializer(serializers.ModelSerializer):
    novel_title = serializers.CharField(source='novel.title', read_only=True)
    reporter_name = serializers.CharField(source='reported_by.username', read_only=True, default='')
    handler_name = serializers.CharField(source='handled_by.username', read_only=True, default='')

    class Meta:
        model = ViolationRecord
        fields = '__all__'


class ChapterUploadLogSerializer(serializers.ModelSerializer):
    novel_title = serializers.CharField(source='novel.title', read_only=True)
    uploader_name = serializers.CharField(source='uploaded_by.username', read_only=True, default='')

    class Meta:
        model = ChapterUploadLog
        fields = '__all__'


class AdvertisementStatsSerializer(AdvertisementSerializer):
    ctr = serializers.SerializerMethodField()

    def get_ctr(self, obj):
        if obj.view_count > 0:
            return round(obj.click_count / obj.view_count * 100, 2)
        return 0

    class Meta(AdvertisementSerializer.Meta):
        fields = AdvertisementSerializer.Meta.fields + ['ctr']


class AdminChapterSerializer(serializers.ModelSerializer):
    novel_title = serializers.CharField(source='novel.title', read_only=True, default='')

    class Meta:
        model = Chapter
        fields = [
            'id', 'novel_id', 'novel_title', 'title', 'content',
            'chapter_order', 'word_count', 'created_at', 'updated_at'
        ]
