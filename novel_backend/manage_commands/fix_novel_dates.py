import django, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'novel_project.settings'
django.setup()
from novels.models import Novel
from django.utils import timezone
from datetime import timedelta

now = timezone.now()
novels = list(Novel.objects.all())
random.seed(42)

# 把15本小说的创建时间分散到过去14天内，模拟陆续上架
for i, n in enumerate(novels):
    days_ago = random.randint(0, 13)
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    n.created_at = now - timedelta(days=days_ago, hours=hours, minutes=minutes)
    n.save(update_fields=['created_at'])

print('已更新15本小说的创建时间到最近14天')
print()
print('=== 近7天每日新增 ===')
today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
for i in range(7):
    day = today_start - timedelta(days=6-i)
    day_end = day + timedelta(days=1)
    c = Novel.objects.filter(created_at__gte=day, created_at__lt=day_end).count()
    label = day.strftime('%m-%d')
    bar = '#' * c
    print(f'  {label}: {c} 本 {bar}')
