from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.CharField(source='user.avatar', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'novel', 'user', 'username', 'user_avatar',
            'content', 'rating', 'created_at',
        ]
        read_only_fields = ['user', 'created_at']

    def validate_content(self, value):
        v = (value or '').strip()
        if not v:
            raise serializers.ValidationError('评论内容不能为空')
        if len(v) > 500:
            raise serializers.ValidationError('评论内容不能超过 500 字')
        return v

    def validate_rating(self, value):
        if value is None:
            return 0
        if value < 0 or value > 5:
            raise serializers.ValidationError('评分必须在 0-5 之间')
        return value
