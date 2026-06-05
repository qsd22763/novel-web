# -*- coding: utf-8 -*-
"""
墨香书阁 — 批量导入小说数据 + 封面匹配脚本
功能：
1. 导入 seed_data.py 全部爬虫小说数据（22本）
2. 额外补充热门小说数据，使总数达到 70+
3. 按书名精准/模糊匹配本地封面图片
4. 新增书籍 audit_status=2（已通过），直接可展示
5. 跳过已存在的书籍（按 title 去重）
"""

import os
import sys
import django
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')
django.setup()

from novels.models import Novel, Chapter
from django.conf import settings

# ── 配置 ──
COVER_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'CopyBook', 'copyBook-master', 'bookspider', 'bookTest', 'cover'
)
MEDIA_COVERS_DIR = os.path.join(settings.MEDIA_ROOT, 'covers')

VALID_CATEGORIES = ['玄幻', '都市', '穿越', '科幻', '游戏', '悬疑', '武侠', '历史']


def get_cover_files():
    """扫描本地封面目录，返回 {文件名(无扩展名): 完整路径}"""
    covers = {}
    if os.path.isdir(COVER_DIR):
        for f in os.listdir(COVER_DIR):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                name = os.path.splitext(f)[0]
                covers[name] = os.path.join(COVER_DIR, f)
    return covers


def match_cover(title, cover_map):
    """
    按书名匹配封面：
    1. 精准匹配：封面文件名 == 书名
    2. 包含匹配：书名包含封面名 或 封面名包含书名
    返回相对路径或空串
    """
    # 精准
    if title in cover_map:
        return _copy_cover_to_media(cover_map[title], title)

    # 包含匹配
    for name, path in cover_map.items():
        if name in title or title in name:
            return _copy_cover_to_media(path, title)

    return ''


def _copy_cover_to_media(src_path, title):
    """将封面复制到 MEDIA/covers/ 目录，返回 URL 路径"""
    try:
        os.makedirs(MEDIA_COVERS_DIR, exist_ok=True)
        ext = os.path.splitext(src_path)[1].lower()
        safe_name = "".join(c for c in title if c.isalnum() or c in ('_', '-'))[:50]
        dst_name = f"{safe_name}{ext}"
        dst_path = os.path.join(MEDIA_COVERS_DIR, dst_name)

        if not os.path.exists(dst_path):
            shutil.copy2(src_path, dst_path)

        return f"{settings.MEDIA_URL}covers/{dst_name}"
    except Exception as e:
        print(f"      ⚠️  封面复制失败: {e}")
        return ''


# ── 数据源：来自 seed_data.py 的爬虫数据（22本）──────────────
SEED_NOVELS = [
    {
        'title': '斗破苍穹', 'author': '天蚕土豆', 'category': '玄幻',
        'description': '这里是斗破苍穹的简介...三十年河东，三十年河西，莫欺少年穷！',
        'status': 1, 'word_count': 500000, 'view_count': 1000000,
        'tags': '玄幻,热血,修炼',
    },
    {
        'title': '完美世界', 'author': '辰东', 'category': '玄幻',
        'description': '一粒尘可填海，一根草斩尽日月星辰...',
        'status': 1, 'word_count': 800000, 'view_count': 800000,
        'tags': '玄幻,冒险,热血',
    },
    {
        'title': '庆余年', 'author': '猫腻', 'category': '穿越',
        'description': '现代金融人士穿越到古代成为赘婿，看他如何翻手为云覆手为雨。',
        'status': 1, 'word_count': 400000, 'view_count': 600000,
        'tags': '穿越,权谋,爽文',
    },
    {
        'title': '凡人修仙传', 'author': '忘语', 'category': '玄幻',
        'description': '一个普通山村小子，偶然之下进入到当地一个小门派...',
        'status': 1, 'word_count': 700000, 'view_count': 700000,
        'tags': '仙侠,修真,凡人流',
    },
    {
        'title': '全职高手', 'author': '蝴蝶蓝', 'category': '游戏',
        'description': '网游荣耀中被誉为教科书级别的顶尖高手叶修...',
        'status': 1, 'word_count': 300000, 'view_count': 500000,
        'tags': '游戏,电竞,热血',
    },
    {
        'title': '赘婿', 'author': '愤怒的香蕉', 'category': '历史',
        'description': '现代金融人士穿越到古代成为赘婿，看他如何翻手为云覆手为雨。',
        'status': 1, 'word_count': 600000, 'view_count': 550000,
        'tags': '历史,穿越,商战',
    },
    {
        'title': '大主宰', 'author': '天蚕土豆', 'category': '玄幻',
        'description': '大千世界，强者如林，且看少年牧尘崛起于大千世界。',
        'status': 1, 'word_count': 650000, 'view_count': 750000,
        'tags': '玄幻,热血,成长',
    },
    {
        'title': '雪中悍刀行', 'author': '烽火戏诸侯', 'category': '武侠',
        'description': '江湖是一张珠帘。大人物小人物，是珠子，大故事小故事，是串线。',
        'status': 1, 'word_count': 500000, 'view_count': 650000,
        'tags': '武侠,江湖,权谋',
    },
    {
        'title': '择天记', 'author': '猫腻', 'category': '玄幻',
        'description': '命里有时终须有，命里无时要强求。这是一个重生者逆天改命的故事。',
        'status': 1, 'word_count': 450000, 'view_count': 500000,
        'tags': '玄幻,逆天改命',
    },
    {
        'title': '仙逆', 'author': '耳根', 'category': '玄幻',
        'description': '顺为凡，逆则仙。逆天改命，我欲成仙。',
        'status': 1, 'word_count': 800000, 'view_count': 850000,
        'tags': '仙侠,修真,逆天',
    },
    {
        'title': '一念永恒', 'author': '耳根', 'category': '玄幻',
        'description': '一念成沧海，一念化桑田。一念斩千魔，一念诛万仙。唯我念……永恒。',
        'status': 1, 'word_count': 700000, 'view_count': 780000,
        'tags': '仙侠,搞笑,修真',
    },
    {
        'title': '星辰变', 'author': '我吃西红柿', 'category': '玄幻',
        'description': '不再平凡的少年秦羽，踏上修炼之路，星辰变，唯我不灭。',
        'status': 1, 'word_count': 600000, 'view_count': 720000,
        'tags': '玄幻,修真,星际',
    },
    {
        'title': '盘龙', 'author': '我吃西红柿', 'category': '玄幻',
        'description': '大小的血睛鬃毛狮，力可拔山的巨熊，鼻息怒吼震八荒的紫晶翼狮王。',
        'status': 1, 'word_count': 550000, 'view_count': 680000,
        'tags': '玄幻,西方奇幻,龙',
    },
    {
        'title': '飞刀之后', 'author': '流浪的蛤蟆', 'category': '武侠',
        'description': '飞刀出，天地惊。小李飞刀之后的故事。',
        'status': 1, 'word_count': 400000, 'view_count': 450000,
        'tags': '武侠,江湖,传承',
    },
    {
        'title': '我欲封天', 'author': '耳根', 'category': '玄幻',
        'description': '我若要有，天不可无。我若要无，天不许有。',
        'status': 1, 'word_count': 750000, 'view_count': 820000,
        'tags': '仙侠,逆天,热血',
    },
    {
        'title': '永夜君王', 'author': '烟雨江南', 'category': '玄幻',
        'description': '永夜将至，王者归来。千夜背负着神秘的使命，踏上王者之路。',
        'status': 1, 'word_count': 650000, 'view_count': 590000,
        'tags': '玄幻,暗夜,王者',
    },
    {
        'title': '校花的贴身高手', 'author': '鱼人二代', 'category': '都市',
        'description': '奉师傅之命，下山保护校花，却不想卷入一场场都市漩涡。',
        'status': 1, 'word_count': 900000, 'view_count': 950000,
        'tags': '都市,校花,保镖',
    },
    {
        'title': '神墓', 'author': '辰东', 'category': '玄幻',
        'description': '远古神魔陵园崩塌，神魔遗体不翼而飞。万年过后，一个少年出现。',
        'status': 1, 'word_count': 700000, 'view_count': 800000,
        'tags': '玄幻,神魔,探险',
    },
    {
        'title': '遮天', 'author': '辰东', 'category': '玄幻',
        'description': '登天路，踏歌行，弹指遮天。九龙拉棺，诠释着星空古路的开启。',
        'status': 1, 'word_count': 750000, 'view_count': 850000,
        'tags': '玄幻,星空,大帝',
    },
    {
        'title': '盗墓笔记', 'author': '南派三叔', 'category': '悬疑',
        'description': '五十年前，长沙土夫子因一件青铜件而引出一段千年古卷。',
        'status': 1, 'word_count': 450000, 'view_count': 880000,
        'tags': '悬疑,盗墓,探险',
    },
    {
        'title': '鬼吹灯', 'author': '天下霸唱', 'category': '悬疑',
        'description': '远古的文明，失落的宝藏，神秘莫测的古墓。',
        'status': 1, 'word_count': 500000, 'view_count': 900000,
        'tags': '悬疑,盗墓,摸金',
    },
    {
        'title': '武动乾坤', 'author': '天蚕土豆', 'category': '玄幻',
        'description': '这里没有魔法，没有斗气，只有武术的中华崛起。',
        'status': 1, 'word_count': 600000, 'view_count': 720000,
        'tags': '玄幻,热血,武学',
    },
]

# ── 补充数据：热门小说（达到 70+ 总量）─────────────────────────
EXTRA_NOVELS = [
    {'title': '元尊', 'author': '天蚕土豆', 'category': '玄幻', 'description': '天蚕土豆新书，讲述少年周元崛起于逆境的故事。', 'status': 1, 'word_count': 550000, 'view_count': 680000, 'tags': '玄幻,元气,逆袭'},
    {'title': '剑来', 'author': '烽火戏诸侯', 'category': '武侠', 'description': '剑来！一个生长在骊窟的孩子，一肩挑起五座书院。', 'status': 1, 'word_count': 800000, 'view_count': 850000, 'tags': '武侠,剑道,书院'},
    {'title': '万古最强宗', 'author': '暗点', 'category': '玄幻', 'description': '这是一个岌岌可危的宗门，却培养出了一堆最强者。', 'status': 1, 'word_count': 500000, 'view_count': 620000, 'tags': '玄幻,宗门,系统'},
    {'title': '诡秘之主', 'author': '爱潜水的乌贼', 'category': '玄幻', 'description': '蒸汽与机械的浪潮中，谁能触及非凡？', 'status': 1, 'word_count': 920000, 'view_count': 1200000, 'tags': '玄幻,克苏鲁,西幻'},
    {'title': '大道朝天', 'author': '猫腻', 'category': '玄幻', 'description': '一道剑光，照亮了整个九州的夜空。', 'status': 1, 'word_count': 780000, 'view_count': 700000, 'tags': '玄幻,仙侠,哲学'},
    {'title': '牧神记', 'author': '宅猪', 'category': '玄幻', 'description': '大墟的祖训说，天黑，别出门。', 'status': 1, 'word_count': 650000, 'view_count': 680000, 'tags': '玄幻,神话,变身'},
    {'title': '帝霸', 'author': '厌笔萧生', 'category': '玄幻', 'description': '千万年后，李七夜重启了当年之路。', 'status': 1, 'word_count': 1100000, 'view_count': 920000, 'tags': '玄幻,无敌,重生'},
    {'title': '龙王传说', 'author': '唐家三少', 'category': '玄幻', 'description': '龙王传说，魂师的世界再次开启新的篇章。', 'status': 1, 'word_count': 480000, 'view_count': 760000, 'tags': '玄幻,斗罗,魂师'},
    {'title': '斗罗大陆', 'author': '唐家三少', 'category': '玄幻', 'description': '唐门外门弟子唐三，因偷学内门绝学而为唐门所不容。', 'status': 1, 'word_count': 520000, 'view_count': 1300000, 'tags': '玄幻,武魂,学院'},
    {'title': '吞噬星空', 'author': '我吃西红柿', 'category': '科幻', 'description': '地球RR病毒爆发后，人类进入基地时代...', 'status': 1, 'word_count': 580000, 'view_count': 690000, 'tags': '科幻,末世,进化'},
    {'title': '莽荒纪', 'author': '我吃西红柿', 'category': '玄幻', 'description': '纪宁死后来到了阴曹地府，获得一次重生机会。', 'status': 1, 'word_count': 490000, 'view_count': 580000, 'tags': '玄幻,转世,修行'},
    {'title': '傲世江湖', 'author': '慕容美', 'category': '武侠', 'description': '江湖路远，刀光剑影间书写一段传奇。', 'status': 1, 'word_count': 380000, 'view_count': 420000, 'tags': '武侠,江湖,传奇'},
    {'title': '邪魔妖道', 'author': '梦入神机', 'category': '玄幻', 'description': '正邪之间，一念成魔。', 'status': 1, 'word_count': 420000, 'view_count': 390000, 'tags': '玄幻,魔道,正邪'},
    {'title': '兽拳', 'author': '静官', 'category': '玄幻', 'description': '以兽炼拳，拳破苍穹。', 'status': 1, 'word_count': 350000, 'view_count': 340000, 'tags': '玄幻,兽类,格斗'},
    {'title': '我的老婆是狐狸精', 'author': '梵缺', 'category': '都市', 'description': '一个平凡男人和狐狸精老婆的爆笑生活。', 'status': 1, 'word_count': 280000, 'view_count': 310000, 'tags': '都市,搞笑,异能'},
    {'title': '武当门徒', 'author': '昙花碎影', 'category': '武侠', 'description': '武当山上少年郎，一剑光寒十九州。', 'status': 1, 'word_count': 320000, 'view_count': 290000, 'tags': '武侠,道教,剑术'},
    {'title': '傅家金龙传奇之少年游', 'author': '古龙', 'category': '武侠', 'description': '傅红雪少年时期的故事，快意恩仇闯荡江湖。', 'status': 1, 'word_count': 360000, 'view_count': 350000, 'tags': '武侠,江湖,少年'},
    {'title': '重生之都市修仙', 'author': '十里剑神', 'category': '都市', 'description': '渡劫期大能陈北玄重生回到高中时代，弥补前世遗憾。', 'status': 1, 'word_count': 850000, 'view_count': 1100000, 'tags': '都市,重生,修仙'},
    {'title': '全职法师', 'author': '乱', 'category': '玄幻', 'description': '一个拥有双系法力的少年，在魔法世界中崛起。', 'status': 1, 'word_count': 620000, 'view_count': 730000, 'tags': '玄幻,魔法,校园'},
    {'title': '修真世界', 'author': '方想', 'category': '玄幻', 'description': '一个现代大学生意外来到修真世界的故事。', 'status': 1, 'word_count': 440000, 'view_count': 490000, 'tags': '玄幻,修真,经营'},
    {'title': '紫川', 'author': '老猪', 'category': '玄幻', 'description': '紫川家族三杰在乱世中的传奇故事。', 'status': 1, 'word_count': 530000, 'view_count': 560000, 'tags': '玄幻,战争,家族'},
    {'title': '佣兵天下', 'author': '说不得大师', 'category': '玄幻', 'description': '三个少年的佣兵传奇之旅。', 'status': 1, 'word_count': 510000, 'view_count': 530000, 'tags': '玄幻,佣兵,冒险'},
    {'title': '悟空传', 'author': '今何在', 'category': '玄幻', 'description': '我要这天，再遮不住我眼；要这地，再埋不了我心。', 'status': 1, 'word_count': 120000, 'view_count': 430000, 'tags': '玄幻,西游,哲理'},
    {'title': '搜神记', 'author': '树下野狐', 'category': '玄幻', 'description': '上古神话时代的宏大史诗。', 'status': 1, 'word_count': 560000, 'view_count': 480000, 'tags': '玄幻,上古,神话'},
    {'title': '蛮荒记', 'author': '树下野狐', 'category': '玄幻', 'description': '搜神记续作，继续太古神话的篇章。', 'status': 1, 'word_count': 540000, 'view_count': 460000, 'tags': '玄幻,太古,神话'},
    {'title': '朱雀记', 'author': '猫腻', 'category': '玄幻', 'description': '一个普通青年被一只朱雀带入修真界的故事。', 'status': 1, 'word_count': 380000, 'view_count': 370000, 'tags': '玄幻,修真,搞笑'},
    {'title': '将夜', 'author': '猫腻', 'category': '玄幻', 'description': '与天斗，其乐无穷。宁缺在长安城的故事。', 'status': 1, 'word_count': 720000, 'view_count': 690000, 'tags': '玄幻,长安,儒道'},
    {'title': '知否知否应是绿肥红瘦', 'author': '关心则乱', 'category': '历史', 'description': '盛家庶女明兰在深宅大院中的生存智慧。', 'status': 1, 'word_count': 680000, 'view_count': 870000, 'tags': '历史,宅斗,古代'},
    {'title': '琅琊榜', 'author': '海宴', 'category': '历史', 'description': '麒麟才子梅长苏复仇雪冤的传奇故事。', 'status': 1, 'word_count': 450000, 'view_count': 930000, 'tags': '历史,权谋,复仇'},
    {'title': '庆余年·远来是客', 'author': '猫腻', 'category': '穿越', 'description': '范闲初入京都，开启了一段波澜壮阔的人生。', 'status': 1, 'word_count': 420000, 'view_count': 710000, 'tags': '穿越,权谋,京都'},
    {'title': '赘婿·金陵风云', 'author': '愤怒的香蕉', 'category': '穿越', 'description': '宁毅在江宁商界的崛起之路。', 'status': 1, 'word_count': 580000, 'view_count': 630000, 'tags': '穿越,商战,江宁'},
    {'title': '末日轮盘', 'author': '幻动', 'category': '科幻', 'description': '末世降临，人类在废土上的求生之旅。', 'status': 1, 'word_count': 360000, 'view_count': 380000, 'tags': '科幻,末世,求生'},
    {'title': '深海余烬', 'author': '远瞳', 'category': '科幻', 'description': '在深海的迷雾中，寻找失落的文明。', 'status': 1, 'word_count': 340000, 'view_count': 350000, 'tags': '科幻,深海,克苏鲁'},
    {'title': '第一序列', 'author': '会说话的肘子', 'category': '科幻', 'description': '废土之上，秩序重建。', 'status': 1, 'word_count': 560000, 'view_count': 610000, 'tags': '科幻,废土,秩序'},
    {'title': '异常生物见闻录', 'author': '远瞳', 'category': '科幻', 'description': '郝仁和他的非正常房客们的日常。', 'status': 1, 'word_count': 420000, 'view_count': 520000, 'tags': '科幻,搞笑,日常'},
    {'title': '惊悚乐园', 'author': '三天两觉', 'category': '游戏', 'description': '一款超越现实的恐怖游戏。', 'status': 1, 'word_count': 780000, 'view_count': 840000, 'tags': '游戏,惊悚,无限流'},
    {'title': '全球高武', 'author': '老鹰吃小鸡', 'category': '游戏', 'description': '全球高武时代，武道通神。', 'status': 1, 'word_count': 640000, 'view_count': 710000, 'tags': '游戏,高武,全球'},
    {'title': '王牌御史', 'author': '佟遥', 'category': '悬疑', 'description': '打更人叶言的双面人生。', 'status': 1, 'word_count': 280000, 'view_count': 330000, 'tags': '悬疑,搞笑,妖怪'},
    {'title': '我有一座恐怖屋', 'author': '我会修空调', 'category': '悬疑', 'description': '陈歌继承了一座鬼屋，从此走上不归路。', 'status': 1, 'word_count': 460000, 'view_count': 670000, 'tags': '悬疑,灵异,恐怖'},
    {'title': '道诡异仙', 'author': '狐尾的笔', 'category': '玄幻', 'description': '在这个诡异的世界里，什么是真实？', 'status': 1, 'word_count': 380000, 'view_count': 590000, 'tags': '玄幻,克苏鲁,诡异'},
    {'title': '宿命之环', 'author': '爱潜水的乌贼', 'category': '玄幻', 'description': '诡秘之主第二部，卢米安·李的全新旅程。', 'status': 1, 'word_count': 320000, 'view_count': 540000, 'tags': '玄幻,西幻,诡秘'},
    {'title': '大奉打更人', 'author': '卖报小郎君', 'category': '玄幻', 'description': '许七安在大奉王朝的探案修仙之旅。', 'status': 1, 'word_count': 850000, 'view_count': 980000, 'tags': '玄幻,探案,搞笑'},
    {'title': '轮回乐园', 'author': '那一只蚊子', 'category': '游戏', 'description': '苏晓穿梭在不同位面的无限流冒险。', 'status': 1, 'word_count': 920000, 'view_count': 890000, 'tags': '游戏,无限流,冒险'},
    {'title': '放开那个女巫', 'author': '二目', 'category': '奇幻', 'description': '程岩带着女巫们在异世界的种田生活。', 'status': 1, 'word_count': 430000, 'view_count': 510000, 'tags': '奇幻,种田,女巫'},
    {'title': '隐杀', 'author': '愤怒的香蕉', 'category': '都市', 'description': '顾惜字的隐秘生活。', 'status': 1, 'word_count': 470000, 'view_count': 530000, 'tags': '都市,隐秘,杀手'},
    {'title': '史上第一混乱', 'author': '张小花', 'category': '穿越', 'description': '荆轲、刘邦、李白等历史人物齐聚现代。', 'status': 1, 'word_count': 390000, 'view_count': 440000, 'tags': '穿越,搞笑,历史人物'},
]


def import_novels(novels_data, cover_map):
    """批量导入小说数据"""
    created = 0
    skipped = 0
    matched_covers = 0

    for data in novels_data:
        title = data['title']

        # 去重：按标题检查是否已存在
        if Novel.objects.filter(title=title).exists():
            skipped += 1
            continue

        # 匹配封面
        cover_url = match_cover(title, cover_map)
        if cover_url:
            matched_covers += 1

        # 分类兜底
        cat = data.get('category', '玄幻')
        if cat not in VALID_CATEGORIES:
            cat = '玄幻'

        novel = Novel.objects.create(
            title=title,
            author=data['author'],
            category=cat,
            description=data.get('description', ''),
            tags=data.get('tags', ''),
            status=data.get('status', 0),
            audit_status=2,  # 已通过审核
            word_count=data.get('word_count', 0),
            view_count=data.get('view_count', 0),
            recommend=0,
            cover=cover_url,
        )
        created += 1
        cover_tag = ' [封面✓]' if cover_url else ''
        print(f"  ✓ [{novel.id}] {title} / {data['author']} / {cat}{cover_tag}")

    return created, skipped, matched_covers


def run():
    print('=' * 64)
    print('  墨香书阁 — 批量小说数据导入工具')
    print('=' * 64)

    # 统计导入前
    before = Novel.objects.count()
    print(f'\n[导入前] 当前数据库小说总数: {before}')

    # 加载封面映射
    cover_map = get_cover_files()
    print(f'[封面] 扫描到 {len(cover_map)} 张本地封面: {list(cover_map.keys())}')

    # 导入种子数据（22本）
    print('\n--- 导入种子数据（爬虫数据） ---')
    c1, s1, m1 = import_novels(SEED_NOVELS, cover_map)

    # 导入补充数据（38本）
    print('\n--- 导入补充数据（热门小说） ---')
    c2, s2, m2 = import_novels(EXTRA_NOVELS, cover_map)

    # 统计
    after = Novel.objects.count()
    total_created = c1 + c2
    total_skipped = s1 + s2
    total_matched = m1 + m2

    print('\n' + '=' * 64)
    print(f'  导入报告')
    print('=' * 64)
    print(f'  导入前总数:     {before}')
    print(f'  新增导入:       {total_created}')
    print(f'  跳过(已存在):   {total_skipped}')
    print(f'  封面匹配成功:   {total_matched}')
    print(f'  导入后总数:     {after}')
    print(f'  审核状态:       全部 audit_status=2 (已通过)')
    print('=' * 64)

    # 分页验证
    page_size = 12
    total_pages = (after + page_size - 1) // page_size
    print(f'\n  分页验证: 每页{page_size}条, 共{total_pages}页')

    # 各状态统计
    from django.db.models import Count
    for s, label in [(0,'草稿'), (1,'待审核'), (2,'已发布'), (3,'驳回')]:
        c = Novel.objects.filter(audit_status=s).count()
        if c > 0:
            print(f'  {label}: {c}')


if __name__ == '__main__':
    run()
