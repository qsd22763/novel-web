import django, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'novel_project.settings'
django.setup()
from novels.models import Comment
from django.utils import timezone
from datetime import timedelta

now = timezone.now()
comments = list(Comment.objects.all())
random.seed(99)

# 把评论创建时间分散到最近14天
for c in comments:
    days_ago = random.randint(0, 13)
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    c.created_at = now - timedelta(days=days_ago, hours=hours, minutes=minutes)
    c.save(update_fields=['created_at'])

print(f'已更新 {len(comments)} 条评论的创建时间到最近14天')
print()
print('=== 近7天每日新增评论 ===')
today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
for i in range(7):
    day = today_start - timedelta(days=6-i)
    day_end = day + timedelta(days=1)
    c = Comment.objects.filter(created_at__gte=day, created_at__lt=day_end).count()
    label = day.strftime('%m-%d')
    bar = '#' * c
    print(f'  {label}: {c} 条 {bar}')
