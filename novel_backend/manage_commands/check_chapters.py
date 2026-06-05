import django, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'novel_project.settings'
django.setup()
from novels.models import Chapter, Novel
from django.db.models import Count

print('总章节数:', Chapter.objects.count())
print()
print('有章节的小说:')
novels_with_chapters = Novel.objects.annotate(ch_count=Count('chapters')).filter(ch_count__gt=0).order_by('-ch_count')
for n in novels_with_chapters:
    print(f'  ID={n.id:<4} | {n.title:<22} | {n.ch_count}章')

print()
print(f'共 {novels_with_chapters.count()} 本小说有章节数据')
