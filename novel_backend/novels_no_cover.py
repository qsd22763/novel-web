import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'novel_project.settings'
django.setup()
from novels.models import Novel

no_cover = list(Novel.objects.filter(cover='') | Novel.objects.filter(cover__isnull=True))
print(f'=== 无封面书籍 ({len(no_cover)}) ===\n')
for i, n in enumerate(no_cover, 1):
    print(f'{i:3}. [{n.category}] {n.title}  (id={n.id})')
