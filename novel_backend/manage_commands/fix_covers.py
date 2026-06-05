# -*- coding: utf-8 -*-
"""
修复脚本：确保所有小说封面使用纯英文路径（避免中文URL编码问题）
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')
django.setup()
from novels.models import Novel

COVER_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media', 'covers')

def run():
    print('=' * 60)
    print('🔧 修复：所有封面使用纯英文路径')
    print('=' * 60)

    # 只收集纯英文编号的封面文件 (cover_XX.jpg)
    safe_covers = []
    for f in sorted(os.listdir(COVER_DIR)):
        if f.startswith('cover_') and f.endswith(('.jpg', '.jpeg', '.png', '.webp')):
            full_path = os.path.join(COVER_DIR, f)
            if os.path.getsize(full_path) > 5000:
                safe_covers.append(f)

    print(f'📁 可用安全封面: {len(safe_covers)} 个 (纯英文命名)\n')

    novels = list(Novel.objects.all().order_by('id'))
    updated = 0
    has_chinese = 0

    for i, novel in enumerate(novels):
        cover_file = safe_covers[i % len(safe_covers)]
        new_cover = f'/media/covers/{cover_file}'

        # 检查旧封面是否含中文
        old_has_chinese = any('\u4e00' <= c <= '\u9fff' for c in novel.cover)

        if new_cover != novel.cover or old_has_chinese:
            novel.cover = new_cover
            novel.save(update_fields=['cover'])
            flag = '🔤' if old_has_chinese else '✅'
            print(f'  {flag} [{novel.id}] {novel.title} → {cover_file}')
            if old_has_chinese:
                has_chinese += 1
            updated += 1
        else:
            print(f'  ⏭️ [{novel.id}] {novel.title} → 无需修改')

    print(f'\n{"="*60}')
    print(f'✅ 完成！更新 {updated} 本, 其中修复中文路径 {has_chinese} 本')
    print(f'   所有封面现在都是 /media/covers/cover_XX.jpg 格式')

if __name__ == '__main__':
    run()
