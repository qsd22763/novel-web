import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'novel_project.settings'
django.setup()
from novels.models import Novel

# 回滚：清除所有 cover_XX.jpg 通用封面，只保留真实书名匹配的
generic_cleared = Novel.objects.filter(cover__startswith='/media/covers/cover_').update(cover='')
print(f'Rolled back generic covers: {generic_cleared} books cleared')

# 验证最终状态
total = Novel.objects.count()
has_cover = Novel.objects.exclude(cover='').exclude(cover__isnull=True).count()
no_cover = total - has_cover

print(f'\nFinal state:')
print(f'  Total novels: {total}')
print(f'  With real cover: {has_cover}')
print(f'  Without cover (empty): {no_cover}')

# 列出有封面的书
if has_cover:
    print(f'\n=== Books with cover ({has_cover}) ===')
    for n in Novel.objects.exclude(cover='').exclude(cover__isnull=True):
        print(f'  [{n.title}] -> {n.cover.split("/")[-1]}')
