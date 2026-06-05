# -*- coding: utf-8 -*-
"""
Django管理命令 - 一次性初始化所有测试数据
功能：
1. 创建测试用户（5个）
2. 创建测试评论（每个小说2-3条）
3. 创建收藏、书签和阅读进度
4. 创建广告和公告数据
5. 同步BookCategory分类树
6. 统一小说category字段
7. 更新book_count统计
8. 创建管理员操作日志
"""

import os, sys, django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')
django.setup()

from novels.models import (
    User, Novel, Chapter, Favorite, ReadingProgress,
    Bookmark, Comment, Advertisement, Announcement,
    OperationLog, BookCategory
)
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, datetime
import random

User = get_user_model()

# 定义有效的分类列表
VALID_CATEGORIES = ['玄幻', '都市', '穿越', '科幻', '游戏', '悬疑', '武侠', '历史']


def create_test_users():
    """步骤1: 创建测试用户"""
    print('\n' + '='*60)
    print('📋 步骤1/8: 创建测试用户')
    print('='*60)

    users_data = [
        {
            'username': 'admin',
            'password': 'Admin123',
            'email': 'admin@novel.com',
            'is_staff': True,
            'is_superuser': True,
            'is_author': False,
            'is_vip': False,
            'pen_name': '',
            'bio': '系统管理员',
        },
        {
            'username': 'author1',
            'password': 'Author123',
            'email': 'author1@novel.com',
            'is_staff': False,
            'is_superuser': False,
            'is_author': True,
            'is_vip': True,
            'pen_name': '墨染青城',
            'bio': '知名网络作家，擅长玄幻题材创作',
        },
        {
            'username': 'author2',
            'password': 'Author456',
            'email': 'author2@novel.com',
            'is_staff': False,
            'is_superuser': False,
            'is_author': True,
            'is_vip': False,
            'pen_name': '剑心通明',
            'bio': '新锐作家，专注都市题材',
        },
        {
            'username': 'reader1',
            'password': 'Reader123',
            'email': 'reader1@novel.com',
            'is_staff': False,
            'is_superuser': False,
            'is_author': False,
            'is_vip': True,
            'pen_name': '',
            'bio': '',
        },
        {
            'username': 'reader2',
            'password': 'Reader456',
            'email': 'reader2@novel.com',
            'is_staff': False,
            'is_superuser': False,
            'is_author': False,
            'is_vip': False,
            'pen_name': '',
            'bio': '',
        },
    ]

    created_users = {}
    try:
        for user_data in users_data:
            username = user_data.pop('username')
            password = user_data.pop('password')

            # 检查用户是否已存在
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                print(f'  ✅ 用户 {username} 已存在，跳过创建')
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    **user_data
                )
                print(f'  ✅ 成功创建用户: {username} (密码: {password})')

            created_users[username] = user

        print(f'\n  📊 测试用户创建完成，共 {len(created_users)} 个用户')
        return created_users

    except Exception as e:
        print(f'  ❌ 创建测试用户失败: {str(e)}')
        return {}


def create_test_comments(users):
    """步骤2: 为每个小说创建2-3条评论"""
    print('\n' + '='*60)
    print('💬 步骤2/8: 创建测试评论')
    print('='*60)

    # 获取所有已发布的小说
    novels = Novel.objects.filter(audit_status=2).order_by('-created_at')[:20]

    if not novels.exists():
        print('  ⚠️  数据库中没有已发布的小说，跳过评论创建')
        return 0

    comment_templates = [
        "这本书太精彩了，情节跌宕起伏！",
        "主角成长线写得很棒，推荐阅读",
        "更新速度可以再快一点吗？期待后续！",
        "文笔流畅，人物刻画生动，非常不错",
        "剧情紧凑，每一章都有惊喜，追更中！",
        "作者大大加油，已经安利给朋友了",
        "世界观设定很新颖，期待更多展开",
        "感情戏写得很细腻，看得我热泪盈眶",
        "战斗场面描写得淋漓尽致，大爱！",
        "这本书是我今年看过最好的作品之一",
    ]

    reader1 = users.get('reader1')
    reader2 = users.get('reader2')

    if not reader1 or not reader2:
        print('  ❌ 缺少reader1或reader2用户，无法创建评论')
        return 0

    total_comments = 0
    try:
        for novel in novels:
            # 为每本小说创建2-3条评论
            num_comments = random.randint(2, 3)
            readers = [reader1, reader2]

            for i in range(num_comments):
                reader = random.choice(readers)
                content = random.choice(comment_templates)

                # 避免重复评论
                if not Comment.objects.filter(
                    novel=novel, user=reader, content=content
                ).exists():
                    comment = Comment.objects.create(
                        novel=novel,
                        user=reader,
                        content=content,
                        rating=random.choice([0, 4, 5]),
                    )
                    total_comments += 1

        print(f'  ✅ 成功创建 {total_comments} 条评论，覆盖 {novels.count()} 本小说')
        return total_comments

    except Exception as e:
        print(f'  ❌ 创建评论失败: {str(e)}')
        return 0


def create_favorites_and_bookmarks(users):
    """步骤3: 创建收藏、书签和阅读进度"""
    print('\n' + '='*60)
    print('🔖 步骤3/8: 创建收藏、书签和阅读进度')
    print('='*60)

    # 获取所有已发布的小说
    novels = list(Novel.objects.filter(audit_status=2).order_by('?')[:10])

    if not novels:
        print('  ⚠️  数据库中没有已发布的小说，跳过收藏创建')
        return {'favorites': 0, 'bookmarks': 0, 'progress': 0}

    reader1 = users.get('reader1')
    reader2 = users.get('reader2')

    if not reader1 or not reader2:
        print('  ❌ 缺少读者用户，无法创建收藏数据')
        return {'favorites': 0, 'bookmarks': 0, 'progress': 0}

    stats = {'favorites': 0, 'bookmarks': 0, 'progress': 0}

    try:
        # reader1收藏3-5本
        reader1_novels = random.sample(novels, min(random.randint(3, 5), len(novels)))
        for novel in reader1_novels:
            fav, created = Favorite.objects.get_or_create(user=reader1, novel=novel)
            if created:
                stats['favorites'] += 1

            # 为每本收藏的小说创建书签
            chapters = list(novel.chapters.filter(publish_status=1)[:5])
            if chapters:
                chapter = random.choice(chapters)
                bookmark, created = Bookmark.objects.get_or_create(
                    user=reader1,
                    novel=novel,
                    chapter=chapter,
                    defaults={
                        'position': random.randint(10, 90),
                        'note': f'看到这里很精彩 - {chapter.title}',
                    }
                )
                if created:
                    stats['bookmarks'] += 1

            # 创建阅读进度
            if chapters:
                progress_chapter = random.choice(chapters)
                ReadingProgress.objects.update_or_create(
                    user=reader1,
                    novel=novel,
                    defaults={
                        'chapter': progress_chapter,
                        'position': random.randint(100, len(chapters[0].content) // 2) if chapters[0].content else 0,
                    }
                )
                stats['progress'] += 1

        # reader2收藏2-3本
        remaining_novels = [n for n in novels if n not in reader1_novels]
        if remaining_novels:
            reader2_novels = random.sample(remaining_novels, min(random.randint(2, 3), len(remaining_novels)))
            for novel in reader2_novels:
                fav, created = Favorite.objects.get_or_create(user=reader2, novel=novel)
                if created:
                    stats['favorites'] += 1

                # 创建书签
                chapters = list(novel.chapters.filter(publish_status=1)[:5])
                if chapters:
                    chapter = random.choice(chapters)
                    bookmark, created = Bookmark.objects.get_or_create(
                        user=reader2,
                        novel=novel,
                        chapter=chapter,
                        defaults={
                            'position': random.randint(10, 90),
                            'note': f'标记位置 - {chapter.title}',
                        }
                    )
                    if created:
                        stats['bookmarks'] += 1

                # 创建阅读进度
                if chapters:
                    progress_chapter = random.choice(chapters)
                    ReadingProgress.objects.update_or_create(
                        user=reader2,
                        novel=novel,
                        defaults={
                            'chapter': progress_chapter,
                            'position': random.randint(100, len(chapters[0].content) // 3) if chapters[0].content else 0,
                        }
                    )
                    stats['progress'] += 1

        print(f'  ✅ 收藏: {stats["favorites"]} | 书签: {stats["bookmarks"]} | 阅读进度: {stats["progress"]}')
        return stats

    except Exception as e:
        print(f'  ❌ 创建收藏/书签失败: {str(e)}')
        return {'favorites': 0, 'bookmarks': 0, 'progress': 0}


def create_advertisements():
    """步骤4: 创建广告数据"""
    print('\n' + '='*60)
    print('📢 步骤4/8: 创建广告数据')
    print('='*60)

    ads_data = [
        {
            'title': 'VIP会员限时特惠',
            'ad_type': 'banner',
            'image_url': 'https://picsum.photos/1200/200?random=1',
            'link_url': '/vip',
            'position': 'home_top',
            'sort_order': 1,
        },
        {
            'title': '新书推荐榜',
            'ad_type': 'banner',
            'image_url': 'https://picsum.photos/1200/200?random=2',
            'link_url': '/rankings',
            'position': 'home_top',
            'sort_order': 2,
        },
        {
            'title': '作家招募计划',
            'ad_type': 'banner',
            'image_url': 'https://picsum.photos/1200/200?random=3',
            'link_url': '/author/register',
            'position': 'home_top',
            'sort_order': 3,
        },
    ]

    total_ads = 0
    try:
        for ad_data in ads_data:
            ad, created = Advertisement.objects.update_or_create(
                title=ad_data['title'],
                defaults={
                    **ad_data,
                    'is_active': True,
                    'start_time': timezone.now(),
                    'end_time': timezone.now() + timedelta(days=30),
                }
            )
            if created or ad.is_active:
                total_ads += 1
                action = '创建' if created else '更新'
                print(f'  ✅ {action}广告: {ad_data["title"]}')

        print(f'  ✅ 广告数据准备完成，共 {total_ads} 条')
        return total_ads

    except Exception as e:
        print(f'  ❌ 创建广告失败: {str(e)}')
        return 0


def create_announcements():
    """步骤4(续): 创建公告数据"""
    print('\n' + '='*60)
    print('📢 步骤4(续): 创建公告数据')
    print('='*60)

    announcements_data = [
        {
            'title': '系统维护通知',
            'content': '尊敬的用户，我们将于本周六凌晨2:00-6:00进行系统维护升级，届时部分功能可能暂时无法使用，请提前安排好阅读计划。给您带来的不便敬请谅解！',
            'announcement_type': 'maintenance',
            'is_pinned': True,
        },
        {
            'title': '新人注册送VIP活动',
            'content': '即日起至月底，新注册用户即可免费获得7天VIP体验资格！享受无广告阅读、专属书架等特权。活动期间邀请好友还可获得额外奖励，快来参与吧！',
            'announcement_type': 'activity',
            'is_pinned': False,
        },
    ]

    total_announcements = 0
    try:
        for ann_data in announcements_data:
            ann, created = Announcement.objects.update_or_create(
                title=ann_data['title'],
                defaults={
                    **ann_data,
                    'is_active': True,
                }
            )
            if created or ann.is_active:
                total_announcements += 1
                action = '创建' if created else '更新'
                pinned_tag = ' [置顶]' if ann_data['is_pinned'] else ''
                print(f'  ✅ {action}公告: {ann_data["title"]}{pinned_tag}')

        print(f'  ✅ 公告数据准备完成，共 {total_announcements} 条')
        return total_announcements

    except Exception as e:
        print(f'  ❌ 创建公告失败: {str(e)}')
        return 0


def sync_book_categories():
    """步骤5: 同步BookCategory分类树"""
    print('\n' + '='*60)
    print('🌳 步骤5/8: 同步BookCategory分类树')
    print('='*60)

    # 定义完整的分类树结构
    categories_tree = [
        {
            'name': '玄幻',
            'color': '#A855F7',
            'description': '包含东方玄幻、西方奇幻等幻想题材作品',
            'children': [
                {'name': '东方玄幻', 'color': '#A855F7', 'description': '以东方文化为背景的玄幻作品'},
            ]
        },
        {
            'name': '都市',
            'color': '#3B82F6',
            'description': '现代都市背景的各类题材小说',
            'children': [
                {'name': '都市生活', 'color': '#3B82F6', 'description': '反映现代都市生活的作品'},
            ]
        },
        {
            'name': '穿越',
            'color': '#EC4899',
            'description': '时空穿越、重生题材作品',
            'children': [
                {'name': '历史穿越', 'color': '#EC4899', 'description': '穿越到历史朝代的作品'},
            ]
        },
        {
            'name': '科幻',
            'color': '#06B6D4',
            'description': '科幻题材作品，包含未来科技、太空探索等',
            'children': []
        },
        {
            'name': '游戏',
            'color': '#22C55E',
            'description': '游戏题材、虚拟现实相关作品',
            'children': [
                {'name': '游戏异界', 'color': '#22C55E', 'description': '游戏世界与异界融合的作品'},
            ]
        },
        {
            'name': '悬疑',
            'color': '#F59E0B',
            'description': '悬疑推理、灵异惊悚类作品',
            'children': []
        },
        {
            'name': '武侠',
            'color': '#EF4444',
            'description': '传统武侠、仙侠类作品',
            'children': []
        },
        {
            'name': '历史',
            'color': '#8B5CF6',
            'description': '历史演义、架空历史类作品',
            'children': []
        },
    ]

    try:
        # 清空现有分类数据
        old_count = BookCategory.objects.count()
        BookCategory.objects.all().delete()
        print(f'  🗑️  已清空原有 {old_count} 条分类数据')

        # 创建新的分类树
        created_categories = {}
        sort_order = 0

        for cat_data in categories_tree:
            sort_order += 1
            parent = BookCategory.objects.create(
                name=cat_data['name'],
                color=cat_data['color'],
                description=cat_data['description'],
                sort_order=sort_order,
                is_active=True,
                parent=None,
            )
            created_categories[cat_data['name']] = parent
            print(f'  ✅ 创建主分类: {cat_data["name"]} ({cat_data["color"]})')

            # 创建子分类
            child_sort = 0
            for child_data in cat_data['children']:
                child_sort += 1
                child = BookCategory.objects.create(
                    name=child_data['name'],
                    color=child_data['color'],
                    description=child_data['description'],
                    sort_order=child_sort,
                    is_active=True,
                    parent=parent,
                )
                created_categories[child_data['name']] = child
                print(f'     └─ 创建子分类: {child_data["name"]}')

        total = BookCategory.objects.count()
        print(f'  📊 分类树同步完成，共 {total} 个分类（{len(categories_tree)}主分类 + {total - len(categories_tree)}子分类）')
        return created_categories

    except Exception as e:
        print(f'  ❌ 同步分类树失败: {str(e)}')
        return {}


def normalize_novel_categories():
    """步骤6: 统一小说的category字段"""
    print('\n' + '='*60)
    print('🔄 步骤6/8: 统一小说category字段')
    print('='*60)

    try:
        novels = Novel.objects.all()
        total = novels.count()
        changed = 0

        for novel in novels:
            if novel.category not in VALID_CATEGORIES:
                old_category = novel.category
                novel.category = '玄幻'
                novel.save(update_fields=['category'])
                changed += 1
                print(f'  🔧 [{novel.id}] "{novel.title}": {old_category or "(空)"} → 玄幻')

        print(f'  ✅ 检查完成: 共 {total} 本小说，修正 {changed} 本')
        return changed

    except Exception as e:
        print(f'  ❌ 统一category字段失败: {str(e)}')
        return 0


def update_book_counts():
    """步骤7: 更新各分类的book_count统计"""
    print('\n' + '='*60)
    print('📊 步骤7/8: 更新book_count统计')
    print('='*60)

    try:
        # 获取所有主分类（parent=None）
        main_categories = BookCategory.objects.filter(parent=None, is_active=True)

        for category in main_categories:
            count = Novel.objects.filter(category=category.name).count()
            category.book_count = count
            category.save(update_fields=['book_count'])
            print(f'  📈 {category.name}: {count} 本小说')

        total_books = sum(c.book_count for c in main_categories)
        print(f'  ✅ 统计完成: 全站共 {total_books} 本已发布小说')
        return total_books

    except Exception as e:
        print(f'  ❌ 更新book_count失败: {str(e)}')
        return 0


def create_operation_logs(admin_user):
    """步骤8: 创建管理员操作日志"""
    print('\n' + '='*60)
    print('📝 步骤8/8: 创建操作日志')
    print('='*60)

    if not admin_user:
        print('  ⚠️  未找到管理员用户，跳过日志创建')
        return 0

    logs_data = [
        {
            'action': 'batch',
            'target_type': 'Novel',
            'target_id': 0,
            'target_name': '批量审核通过',
            'detail': '系统自动审核通过了10本待审核的小说',
        },
        {
            'action': 'update',
            'target_type': 'BookCategory',
            'target_id': 1,
            'target_name': '分类树同步',
            'detail': '执行了分类树同步操作，重建了所有分类数据',
        },
        {
            'action': 'import',
            'target_type': 'Chapter',
            'target_id': 0,
            'target_name': '章节批量导入',
            'detail': '成功导入了500个章节数据',
        },
        {
            'action': 'publish',
            'target_type': 'Announcement',
            'target_id': 1,
            'target_name': '发布公告',
            'detail': '发布了新人注册送VIP活动的公告',
        },
        {
            'action': 'ban',
            'target_type': 'User',
            'target_id': 999,
            'target_name': '违规账号封禁',
            'detail': '因发布垃圾广告内容封禁用户账号',
        },
    ]

    total_logs = 0
    try:
        for i, log_data in enumerate(logs_data):
            log = OperationLog.objects.create(
                user=admin_user,
                **log_data,
                ip_address='127.0.0.1',
                user_agent='Admin Management Console',
                created_at=timezone.now() - timedelta(hours=i+1),
            )
            total_logs += 1
            print(f'  ✅ 创建日志: [{log.action}] {log.target_name}')

        print(f'  ✅ 操作日志创建完成，共 {total_logs} 条')
        return total_logs

    except Exception as e:
        print(f'  ❌ 创建操作日志失败: {str(e)}')
        return 0


def run():
    """
    主函数 - 执行所有数据初始化任务
    """
    print('\n' + '#' * 60)
    print('#' + ' ' * 58 + '#')
    print('#     🚀 小说平台测试数据一键初始化工具     #')
    print('#' + ' ' * 58 + '#')
    print('#' * 60)
    print(f'⏰ 开始时间: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}')

    start_time = timezone.now()

    # ==================== 步骤1: 创建测试用户 ====================
    users = create_test_users()
    admin_user = users.get('admin')

    # ==================== 步骤2: 创建评论 ====================
    comment_count = create_test_comments(users)

    # ==================== 步骤3: 创建收藏和书签 ====================
    favorite_stats = create_favorites_and_bookmarks(users)

    # ==================== 步骤4: 创建广告和公告 ====================
    ad_count = create_advertisements()
    announcement_count = create_announcements()

    # ==================== 步骤5: 同步分类树 ====================
    categories = sync_book_categories()

    # ==================== 步骤6: 统一category字段 ====================
    normalized_count = normalize_novel_categories()

    # ==================== 步骤7: 更新统计 ====================
    book_total = update_book_counts()

    # ==================== 步骤8: 创建操作日志 ====================
    log_count = create_operation_logs(admin_user)

    # ==================== 输出汇总报告 ====================
    end_time = timezone.now()
    duration = (end_time - start_time).total_seconds()

    print('\n' + '#' * 60)
    print('#                  📋 初始化完成报告                   #')
    print('#' * 60)
    print(f'''
  👤 测试用户:      {len(users)} 个
  💬 评论数据:      {comment_count} 条
  ❤️  收藏记录:      {favorite_stats.get("favorites", 0)} 条
  🔖 书签记录:      {favorite_stats.get("bookmarks", 0)} 条
  📖 阅读进度:      {favorite_stats.get("progress", 0)} 条
  📢 广告数据:      {ad_count} 条
  📢 公告数据:      {announcement_count} 条
  🌳 分类树:        {len(categories)} 个节点
  🔧 分类修正:      {normalized_count} 本小说
  📊 书籍统计:      {book_total} 本
  📝 操作日志:      {log_count} 条
    ''')
    print(f'⏱️  总耗时: {duration:.2f} 秒')
    print(f'✅ 测试数据创建完成！时间: {end_time.strftime("%Y-%m-%d %H:%M:%S")}')
    print('#' * 60 + '\n')


if __name__ == '__main__':
    run()
