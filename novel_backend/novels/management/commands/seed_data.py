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
                'cover': 'https://img.moèlie.com/covers/yx/doupocangqiong.jpg',
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
                'cover': 'https://img.moèlie.com/covers/yx/wanmeishijie.jpg',
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
                'cover': 'https://img.moèlie.com/covers/yx/qingyunian.jpg',
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
                'cover': 'https://img.moèlie.com/covers/yx/fanrenxiuxian.jpg',
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
                'cover': 'https://img.moèlie.com/covers/yx/quanzhigaoshou.jpg',
                'word_count': 300000,
                'view_count': 500000,
                'chapters': [
                    '第一章 叶修',
                    '第二章 荣耀',
                ]
            },
            {
                'title': '赘婿',
                'author': '愤怒的香蕉',
                'category': '历史',
                'status': 1,
                'description': '现代金融人士穿越到古代成为赘婿，看他如何翻手为云覆手为雨。',
                'cover': 'https://img.moèlie.com/covers/xs/zhuiXu.jpg',
                'word_count': 600000,
                'view_count': 550000,
                'chapters': [
                    '第一章 猎户家的赘婿',
                    '第二章 苏家布坊',
                    '第三章 武朝风云',
                ]
            },
            {
                'title': '大主宰',
                'author': '天蚕土豆',
                'category': '玄幻',
                'status': 1,
                'description': '大千世界，强者如林，且看少年牧尘崛起于大千世界。',
                'cover': 'https://img.moèlie.com/covers/yx/dazuizhu.jpg',
                'word_count': 650000,
                'view_count': 750000,
                'chapters': [
                    '第一章 北灵院',
                    '第二章 灵脉',
                    '第三章 柳域狩猎',
                ]
            },
            {
                'title': '雪中悍刀行',
                'author': '烽火戏诸侯',
                'category': '武侠',
                'status': 1,
                'description': '江湖是一张珠帘。大人物小人物，是珠子，大故事小故事，是串线。',
                'cover': 'https://img.moèlie.com/covers/wx/xuezhong.jpg',
                'word_count': 500000,
                'view_count': 650000,
                'chapters': [
                    '第一章 白衣兵仙',
                    '第二章 徐凤年',
                    '第三章 武帝城',
                ]
            },
            {
                'title': '择天记',
                'author': '猫腻',
                'category': '玄幻',
                'status': 1,
                'description': '命里有时终须有，命里无时要强求。这是一个重生者逆天改命的故事。',
                'cover': 'https://img.moèlie.com/covers/xs/zetianji.jpg',
                'word_count': 450000,
                'view_count': 500000,
                'chapters': [
                    '第一章 随心意',
                    '第二章 黄金主',
                    '第三章 追杀',
                ]
            },
            {
                'title': '仙逆',
                'author': '耳根',
                'category': '仙侠',
                'status': 1,
                'description': '顺为凡，逆则仙。逆天改命，我欲成仙。',
                'cover': 'https://img.moèlie.com/covers/xx/xianni.jpg',
                'word_count': 800000,
                'view_count': 850000,
                'chapters': [
                    '第一章 顺则凡，逆则仙',
                    '第二章 恒岳派',
                    '第三章 修仙之路',
                ]
            },
            {
                'title': '一念永恒',
                'author': '耳根',
                'category': '仙侠',
                'status': 1,
                'description': '一念成沧海，一念化桑田。一念斩千魔，一念诛万仙。唯我念……永恒。',
                'cover': 'https://img.moèlie.com/covers/xx/yinianyongheng.jpg',
                'word_count': 700000,
                'view_count': 780000,
                'chapters': [
                    '第一章 白小纯',
                    '第二章 灵溪宗',
                    '第三章 侯小妹',
                ]
            },
            {
                'title': '星辰变',
                'author': '我吃西红柿',
                'category': '玄幻',
                'status': 1,
                'description': '不再平凡的少年秦羽，踏上修炼之路，星辰变，唯我不灭。',
                'cover': 'https://img.moèlie.com/covers/yx/xingchenbian.jpg',
                'word_count': 600000,
                'view_count': 720000,
                'chapters': [
                    '第一章 秦羽',
                    '第二章 丹田',
                    '第三章 流星',
                ]
            },
            {
                'title': '盘龙',
                'author': '我吃西红柿',
                'category': '玄幻',
                'status': 1,
                'description': '大小的血睛鬃毛狮，力可拔山的巨熊，鼻息怒吼震八荒的紫晶翼狮王。',
                'cover': 'https://img.moèlie.com/covers/yx/panlong.jpg',
                'word_count': 550000,
                'view_count': 680000,
                'chapters': [
                    '第一章 乌山镇',
                    '第二章 盘龙戒指',
                    '第三章 玉兰大陆',
                ]
            },
            {
                'title': '飞刀之后',
                'author': '流浪的蛤蟆',
                'category': '武侠',
                'status': 1,
                'description': '飞刀出，天地惊。小李飞刀之后的故事。',
                'cover': 'https://img.moèlie.com/covers/wx/feidaozhihou.jpg',
                'word_count': 400000,
                'view_count': 450000,
                'chapters': [
                    '第一章 飞刀再现',
                    '第二章 青龙会',
                    '第三章 江湖路',
                ]
            },
            {
                'title': '我欲封天',
                'author': '耳根',
                'category': '仙侠',
                'status': 1,
                'description': '我若要有，天不可无。我若要无，天不许有。',
                'cover': 'https://img.moèlie.com/covers/xx/woyufengtian.jpg',
                'word_count': 750000,
                'view_count': 820000,
                'chapters': [
                    '第一章 封妖正文',
                    '第二章 靠山宗',
                    '第三章 孟浩',
                ]
            },
            {
                'title': '永夜君王',
                'author': '烟雨江南',
                'category': '玄幻',
                'status': 1,
                'description': '永夜将至，王者归来。千夜背负着神秘的使命，踏上王者之路。',
                'cover': 'https://img.moèlie.com/covers/yx/yongyejunshe.jpg',
                'word_count': 650000,
                'view_count': 590000,
                'chapters': [
                    '第一章 永夜',
                    '第二章 帝国',
                    '第三章 黑翼',
                ]
            },
            {
                'title': '校花的贴身高手',
                'author': '鱼人二代',
                'category': '都市',
                'status': 1,
                'description': '奉师傅之命，下山保护校花，却不想卷入一场场都市漩涡。',
                'cover': 'https://img.moèlie.com/covers/ds/xiaohua.jpg',
                'word_count': 900000,
                'view_count': 950000,
                'chapters': [
                    '第一章 高手下山',
                    '第二章 校花楚梦瑶',
                    '第三章 保镖任务',
                ]
            },
            {
                'title': '神墓',
                'author': '辰东',
                'category': '玄幻',
                'status': 1,
                'description': '远古神魔陵园崩塌，神魔遗体不翼而飞。万年过后，一个少年出现。',
                'cover': 'https://img.moèlie.com/covers/yx/shenmu.jpg',
                'word_count': 700000,
                'view_count': 800000,
                'chapters': [
                    '第一章 远古神墓',
                    '第二章 辰南',
                    '第三章 辰家',
                ]
            },
            {
                'title': '遮天',
                'author': '辰东',
                'category': '仙侠',
                'status': 1,
                'description': '登天路，踏歌行，弹指遮天。九龙拉棺，诠释着星空古路的开启。',
                'cover': 'https://img.moèlie.com/covers/xx/zheyantian.jpg',
                'word_count': 750000,
                'view_count': 850000,
                'chapters': [
                    '第一章 九龙拉棺',
                    '第二章 荒古石刻',
                    '第三章 狠人大帝',
                ]
            },
            {
                'title': '盗墓笔记',
                'author': '南派三叔',
                'category': '悬疑',
                'status': 1,
                'description': '五十年前，长沙土夫子因一件青铜件而引出一段千年古卷。',
                'cover': 'https://img.moèlie.com/covers/xy/daomubiji.jpg',
                'word_count': 450000,
                'view_count': 880000,
                'chapters': [
                    '第一章 青铜鼎',
                    '第二章 七星鲁王',
                    '第三章 血尸',
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
                        content=f'这是《{novel.title}》{chapter_title}的内容。\n\n主角在这个世界里经历了许多冒险。他遇到了各种挑战，但凭借着坚韧不拔的意志和过人的智慧，一次次化险为夷。\n\n这一天，他来到了一个新的地方。这里有着神秘的古老传说，也有着未知的危险。但是，他并没有退缩，而是勇敢地迎接了上去。\n\n在这个充满未知的世界里，主角不断地成长和进步。他学会了如何面对困难，如何与他人合作，如何在逆境中保持冷静。\n\n每一个故事都是一段旅程，每一次成长都是一次蜕变。这就是他的传奇，一个平凡少年成长为绝世强者的故事。',
                        chapter_order=i + 1,
                        word_count=3000
                    )
                self.stdout.write(f'  -> 创建 {len(chapters_data)} 个章节')
            else:
                self.stdout.write(f'小说已存在: {novel.title}')

        self.stdout.write(self.style.SUCCESS('测试数据创建完成!'))