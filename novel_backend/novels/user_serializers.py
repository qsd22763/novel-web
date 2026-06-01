from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Favorite, ReadingProgress, Bookmark


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar', 'phone', 'is_vip', 'vip_expire_date', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '两次密码不一致'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('用户名或密码错误')
        if not user.is_active:
            raise serializers.ValidationError('用户已被禁用')
        data['user'] = user
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    novel_title = serializers.CharField(source='novel.title', read_only=True)
    novel_author = serializers.CharField(source='novel.author', read_only=True)
    novel_cover = serializers.CharField(source='novel.cover', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'novel', 'novel_title', 'novel_author', 'novel_cover', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ReadingProgressSerializer(serializers.ModelSerializer):
    novel_title = serializers.CharField(source='novel.title', read_only=True)
    novel_cover = serializers.CharField(source='novel.cover', read_only=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)

    class Meta:
        model = ReadingProgress
        fields = ['id', 'user', 'novel', 'chapter', 'novel_title', 'novel_cover', 'chapter_title', 'position', 'updated_at']
        read_only_fields = ['id', 'user', 'updated_at']


class BookmarkSerializer(serializers.ModelSerializer):
    novel_title = serializers.CharField(source='novel.title', read_only=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'novel', 'chapter', 'position', 'novel_title', 'chapter_title', 'note', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
