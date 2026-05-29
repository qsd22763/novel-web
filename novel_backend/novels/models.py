from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.URLField(max_length=255, blank=True, default='', verbose_name='头像')
    phone = models.CharField(max_length=20, blank=True, default='', verbose_name='手机号')
    is_vip = models.BooleanField(default=False, verbose_name='是否VIP会员')
    vip_expire_date = models.DateTimeField(null=True, blank=True, verbose_name='VIP到期时间')
    is_author = models.BooleanField(default=False, verbose_name='是否作者')
    pen_name = models.CharField(max_length=50, blank=True, default='', verbose_name='笔名')
    bio = models.CharField(max_length=200, blank=True, default='', verbose_name='作者简介')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户'


class Novel(models.Model):
    STATUS_CHOICES = [
        (0, '连载中'),
        (1, '已完结'),
        (2, '已下架'),
    ]
    AUDIT_CHOICES = [
        (0, '草稿'),
        (1, '审核中'),
        (2, '已发布'),
        (3, '驳回'),
    ]

    title = models.CharField(max_length=100, verbose_name='书名')
    author = models.CharField(max_length=50, verbose_name='作者')
    author_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='works', verbose_name='作者账号'
    )
    cover = models.CharField(max_length=500, blank=True, default='', verbose_name='封面')
    description = models.TextField(blank=True, verbose_name='简介')
    category = models.CharField(max_length=20, verbose_name='分类')
    tags = models.CharField(max_length=200, blank=True, default='', verbose_name='标签(逗号分隔)')
    status = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='连载状态')
    audit_status = models.IntegerField(choices=AUDIT_CHOICES, default=2, verbose_name='审核状态')
    word_count = models.IntegerField(default=0, verbose_name='总字数')
    view_count = models.IntegerField(default=0, verbose_name='阅读量')
    recommend = models.IntegerField(default=0, verbose_name='推荐票')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'novel'
        ordering = ['-updated_at']
        verbose_name = '小说'
        verbose_name_plural = '小说'


class Chapter(models.Model):
    PUBLISH_CHOICES = [
        (0, '草稿'),
        (1, '已发布'),
        (2, '已下架'),
    ]

    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='chapters', verbose_name='所属小说')
    title = models.CharField(max_length=100, verbose_name='章节标题')
    content = models.TextField(verbose_name='章节内容')
    chapter_order = models.IntegerField(default=0, verbose_name='章节序号')
    word_count = models.IntegerField(default=0, verbose_name='章节字数')
    publish_status = models.IntegerField(choices=PUBLISH_CHOICES, default=1, verbose_name='发布状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'chapter'
        ordering = ['chapter_order']
        verbose_name = '章节'
        verbose_name_plural = '章节'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='用户')
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='favorites', verbose_name='小说')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')

    class Meta:
        db_table = 'favorite'
        unique_together = ['user', 'novel']
        verbose_name = '收藏'
        verbose_name_plural = '收藏'


class ReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_progress', verbose_name='用户')
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, verbose_name='小说')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, verbose_name='章节')
    position = models.IntegerField(default=0, verbose_name='阅读位置')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'reading_progress'
        unique_together = ['user', 'novel']
        verbose_name = '阅读进度'
        verbose_name_plural = '阅读进度'


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks', verbose_name='用户')
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='bookmarks', verbose_name='小说')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, verbose_name='章节')
    note = models.CharField(max_length=200, blank=True, default='', verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'bookmark'
        ordering = ['-created_at']
        verbose_name = '书签'
        verbose_name_plural = '书签'


class Comment(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='comments', verbose_name='小说')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='用户')
    content = models.CharField(max_length=500, verbose_name='评论内容')
    rating = models.IntegerField(default=0, verbose_name='评分(0-5,0表示纯评论)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发表时间')

    class Meta:
        db_table = 'comment'
        ordering = ['-created_at']
        verbose_name = '评论'
        verbose_name_plural = '评论'
