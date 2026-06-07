from django.contrib.auth.models import AbstractUser
from django.db import models


class AdminUser(models.Model):
    username = models.CharField(max_length=50, unique=True, verbose_name='管理员账号')
    password = models.CharField(max_length=128, verbose_name='密码')
    real_name = models.CharField(max_length=50, blank=True, default='', verbose_name='真实姓名')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='最后登录时间')

    class Meta:
        db_table = 'admin_user'
        verbose_name = '管理员'
        verbose_name_plural = '管理员'

    # ── Django Auth 体系兼容属性 ──
    @property
    def is_authenticated(self):
        return True

    @property
    def is_staff(self):
        return True

    @property
    def is_superuser(self):
        return True

    def get_username(self):
        return self.username

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)


class EmailVerificationCode(models.Model):
    email = models.EmailField(verbose_name='邮箱地址')
    code = models.CharField(max_length=6, verbose_name='验证码')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    is_used = models.BooleanField(default=False, verbose_name='是否已使用')

    class Meta:
        db_table = 'email_verification_code'
        verbose_name = '邮箱验证码'
        verbose_name_plural = '邮箱验证码'

    @property
    def is_expired(self):
        from django.utils import timezone
        import datetime
        return timezone.now() > self.created_at + datetime.timedelta(minutes=5)

    @classmethod
    def generate_and_save(cls, email):
        import random
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        cls.objects.filter(email=email).update(is_used=True)
        return cls.objects.create(email=email, code=code), code

    @classmethod
    def verify(cls, email, code):
        try:
            record = cls.objects.get(email=email, code=code, is_used=False)
            if record.is_expired:
                return False, '验证码已过期，请重新获取'
            record.is_used = True
            record.save(update_fields=['is_used'])
            return True, '验证成功'
        except cls.DoesNotExist:
            return False, '验证码错误'


class User(AbstractUser):
    avatar = models.URLField(max_length=255, blank=True, default='', verbose_name='头像')
    phone = models.CharField(max_length=20, blank=True, default='', verbose_name='手机号')
    is_vip = models.BooleanField(default=False, verbose_name='是否VIP会员')
    vip_expire_date = models.DateTimeField(null=True, blank=True, verbose_name='VIP到期时间')
    is_author = models.BooleanField(default=False, verbose_name='是否作者')
    pen_name = models.CharField(max_length=50, blank=True, default='', verbose_name='笔名')
    bio = models.CharField(max_length=200, blank=True, default='', verbose_name='作者简介')
    coins = models.IntegerField(default=0, verbose_name='虚拟币余额')
    qq_openid = models.CharField(max_length=64, blank=True, default='', verbose_name='QQ OpenID', db_index=True)
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
    audit_status = models.IntegerField(choices=AUDIT_CHOICES, default=1, verbose_name='审核状态')
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
    position = models.IntegerField(default=0, verbose_name='阅读位置(%)')
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


class Advertisement(models.Model):
    AD_TYPE_CHOICES = [
        ('banner', '横幅广告'),
        ('popup', '弹窗广告'),
        ('sidebar', '侧边栏广告'),
    ]
    POSITION_CHOICES = [
        ('home_top', '首页顶部'),
        ('home_sidebar', '首页侧边栏'),
        ('reader_bottom', '阅读页底部'),
        ('reader_popup', '阅读页弹窗'),
    ]

    title = models.CharField(max_length=200, verbose_name='广告标题')
    ad_type = models.CharField(max_length=20, choices=AD_TYPE_CHOICES, verbose_name='广告类型')
    image_url = models.URLField(max_length=500, verbose_name='图片地址')
    link_url = models.URLField(max_length=500, blank=True, default='', verbose_name='跳转链接')
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, verbose_name='展示位置')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    click_count = models.IntegerField(default=0, verbose_name='点击次数')
    view_count = models.IntegerField(default=0, verbose_name='曝光次数')
    sort_order = models.IntegerField(default=0, verbose_name='排序权重')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'advertisement'
        ordering = ['sort_order', '-created_at']
        verbose_name = '广告'
        verbose_name_plural = '广告'


class Announcement(models.Model):
    ANNOUNCEMENT_TYPE_CHOICES = [
        ('notice', '通知'),
        ('maintenance', '维护公告'),
        ('activity', '活动公告'),
    ]

    title = models.CharField(max_length=200, verbose_name='公告标题')
    content = models.TextField(verbose_name='公告内容')
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPE_CHOICES, default='notice', verbose_name='公告类型')
    is_pinned = models.BooleanField(default=False, verbose_name='是否置顶')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'announcement'
        ordering = ['-is_pinned', '-created_at']
        verbose_name = '公告'
        verbose_name_plural = '公告'


class OperationLog(models.Model):
    ACTION_CHOICES = [
        ('create', '创建'), ('update', '更新'), ('delete', '删除'),
        ('batch', '批量操作'), ('import', '导入'),
        ('ban', '封禁'), ('unban', '解禁'),
        ('publish', '发布'), ('withdraw', '撤回'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='operation_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_type = models.CharField(max_length=50)
    target_id = models.IntegerField()
    target_name = models.CharField(max_length=200, blank=True, default='')
    detail = models.TextField(blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'operation_log'
        ordering = ['-created_at']


class BookCategory(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    color = models.CharField(max_length=7, default='#3B82F6')
    description = models.TextField(blank=True, default='')
    book_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'book_category'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class ViolationRecord(models.Model):
    REASON_CHOICES = [
        ('illegal_content', '违法违规内容'),
        ('copyright', '版权侵权'),
        ('spam', '垃圾广告/刷量'),
        ('pornography', '色情低俗'),
        ('violence', '暴力血腥'),
        ('other', '其他违规'),
    ]

    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='violations')
    reason_type = models.CharField(max_length=30, choices=REASON_CHOICES)
    reason_detail = models.TextField()
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reported_violations')
    handled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_violations')
    is_resolved = models.BooleanField(default=False)
    ban_duration_days = models.IntegerField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolve_note = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'violation_record'
        ordering = ['-created_at']


class ChapterUploadLog(models.Model):
    STATUS_CHOICES = [('pending', '待处理'), ('success', '成功'), ('failed', '失败')]

    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='upload_logs')
    filename = models.CharField(max_length=200)
    total_chapters = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    error_log = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chapter_upload_log'
        ordering = ['-created_at']


# ── 签到模块 ──

class CheckInConfig(models.Model):
    """签到奖励配置（全局单例）"""
    daily_reward = models.IntegerField(default=10, verbose_name='每日签到奖励币数')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'checkin_config'

    @classmethod
    def get_config(cls):
        obj, _ = cls.objects.get_or_create(id=1, defaults={'daily_reward': 10})
        return obj


class CheckIn(models.Model):
    """用户签到记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkins')
    check_date = models.DateField(verbose_name='签到日期')
    reward_coins = models.IntegerField(default=0, verbose_name='获得虚拟币')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='签到时间')

    class Meta:
        db_table = 'checkin'
        unique_together = ['user', 'check_date']
        ordering = ['-check_date']


# ── 会员充值模块 ──

MEMBERSHIP_PLAN_CHOICES = [
    ('monthly', '月卡'),
    ('quarterly', '季卡'),
    ('yearly', '年卡'),
]
ORDER_STATUS_CHOICES = [
    ('pending', '待支付'),
    ('paid', '已支付'),
    ('expired', '已过期'),
    ('cancelled', '已取消'),
]


class MembershipOrder(models.Model):
    """会员充值订单"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membership_orders')
    order_no = models.CharField(max_length=32, unique=True, verbose_name='订单号')
    plan_type = models.CharField(max_length=20, choices=MEMBERSHIP_PLAN_CHOICES, verbose_name='套餐类型')
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='金额(元)')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending', verbose_name='状态')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='支付时间')
    expire_at = models.DateTimeField(null=True, blank=True, verbose_name='会员到期时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'membership_order'
        ordering = ['-created_at']


class UserFollow(models.Model):
    """用户关注作者"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follows', verbose_name='用户')
    author_name = models.CharField(max_length=50, verbose_name='作者名')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='关注时间')

    class Meta:
        db_table = 'user_follow'
        unique_together = [['user', 'author_name']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} 关注 {self.author_name}'


class NovelRating(models.Model):
    """小说评分"""
    novel = models.ForeignKey('Novel', on_delete=models.CASCADE, related_name='ratings', verbose_name='小说')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings', verbose_name='用户')
    score = models.PositiveSmallIntegerField(verbose_name='评分(1-5)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评分时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'novel_rating'
        unique_together = [['user', 'novel']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} 给《{self.novel.title}》评了 {self.score} 分'
