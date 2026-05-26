from django.core.management.base import BaseCommand
from novels.models import Novel, Chapter


class Command(BaseCommand):
    help = '创建测试数据'

    def handle(self, *args, **options):
        self.stdout.write('开始创建测试数据...')

        novels_data = [
            {
                'title': '斗破苍穹',
                'author': '天蚕土豆',
                'category': '玄幻',
                'status': 1,
                'description': '这里是斗破苍穹的简介...',
                'word_count': 500000,
                'view_count': 1000000,
                'chapters': [
                    '第一章 陨落的天才',
                    '第二章 筑基丹',
                    '第三章 修炼',
                    '第四章 药老',
                    '第五章 炼药',
                ]
            },
            {
                'title': '完美世界',
                'author': '辰东',
                'category': '玄幻',
                'status': 1,
                'description': '这里是完美世界的简介...',
                'word_count': 800000,
                'view_count': 800000,
                'chapters': [
                    '第一章 荒域',
                    '第二章 石村',
                    '第三章 祭灵',
                ]
            },
            {
                'title': '庆余年',
                'author': '猫腻',
                'category': '穿越',
                'status': 1,
                'description': '这里是庆余年的简介...',
                'word_count': 400000,
                'view_count': 600000,
                'chapters': [
                    '第一章 范建',
                    '第二章 儋州',
                ]
            },
            {
                'title': '凡人修仙传',
                'author': '忘语',
                'category': '仙侠',
                'status': 1,
                'description': '这里是凡人修仙传的简介...',
                'word_count': 700000,
                'view_count': 700000,
                'chapters': [
                    '第一章 山村',
                    '第二章 七玄门',
                ]
            },
            {
                'title': '全职高手',
                'author': '蝴蝶蓝',
                'category': '游戏',
                'status': 1,
                'description': '这里是全职高手的简介...',
                'word_count': 300000,
                'view_count': 500000,
                'chapters': [
                    '第一章 叶修',
                    '第二章 荣耀',
                ]
            },
        ]

        for novel_data in novels_data:
            chapters_data = novel_data.pop('chapters')
            novel, created = Novel.objects.get_or_create(
                title=novel_data['title'],
                defaults=novel_data
            )
            if created:
                self.stdout.write(f'创建小说: {novel.title}')
                for i, chapter_title in enumerate(chapters_data):
                    Chapter.objects.create(
                        novel=novel,
                        title=chapter_title,
                        content=f'这是《{novel.title}》{chapter_title}的内容。\n\n这是一段测试内容，用于演示阅读功能。实际项目中，这里会包含完整的章节内容。',
                        chapter_order=i + 1,
                        word_count=3000
                    )
                self.stdout.write(f'  -> 创建 {len(chapters_data)} 个章节')
            else:
                self.stdout.write(f'小说已存在: {novel.title}')

        self.stdout.write(self.style.SUCCESS('测试数据创建完成!'))
