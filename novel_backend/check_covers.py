import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')
django.setup()
from novels.models import Novel

COVER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'covers')

print(f'{"ID":>3} | {"Size":>6} | {"Title":30s} | Status')
print('-'*70)

bad = []
for novel in Novel.objects.filter(id__gte=88).order_by('id'):
    fname = f'cover_{novel.id:02d}.jpg'
    fpath = os.path.join(COVER_DIR, fname)
    if not os.path.exists(fpath):
        print(f'{novel.id:3d} | MISSING | {novel.title[:28]:28s} | NO FILE')
        bad.append(novel.id)
        continue
    size = os.path.getsize(fpath)
    status = 'OK'
    if size < 3000:
        status = 'TOO_SMALL!'
        bad.append(novel.id)
    elif size > 500000:
        status = 'HUGE(HTML?)'
        bad.append(novel.id)
    print(f'{novel.id:3d} | {size:5d}B | {novel.title[:28]:28s} | {status}')

print(f'\nBad covers ({len(bad)}): {bad}')
