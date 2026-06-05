import os, django, random
os.environ['DJANGO_SETTINGS_MODULE'] = 'novel_project.settings'
django.setup()
from novels.models import Novel

cover_dir = 'media/covers'
files = [f for f in os.listdir(cover_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

# Generic cover pool (cover_01.jpg ~ cover_165.jpg)
generic = sorted([f for f in files if f.startswith('cover_')])
print(f'Generic cover pool: {len(generic)}')

# Named covers for exact/fuzzy match
named_files = {os.path.splitext(f)[0]: f for f in files if not f.startswith('cover_')}

novels = list(Novel.objects.all())
matched = 0
generic_idx = 0

for n in novels:
    if n.cover:
        continue
    if not n.title or len(n.title) < 2:
        continue

    # Strategy 1: exact match
    found = False
    for ext in ('.jpg', '.jpeg', '.png'):
        fname = n.title + ext
        if fname in named_files.values() or fname in files:
            n.cover = '/media/covers/' + fname
            found = True
            break

    # Strategy 2: substring match
    if not found:
        for base, f in named_files.items():
            if n.title in base or base.startswith(n.title):
                n.cover = '/media/covers/' + f
                found = True
                break

    # Strategy 3: assign from generic pool
    if not found and generic:
        assigned = generic[generic_idx % len(generic)]
        n.cover = '/media/covers/' + assigned
        generic_idx += 1
        found = True

    if found:
        n.save(update_fields=['cover'])
        matched += 1

total = Novel.objects.count()
has_cover = Novel.objects.exclude(cover='').exclude(cover__isnull=True).count()
print(f'\nMatched this round: {matched}')
print(f'Total with cover: {has_cover}/{total}')
print(f'Still empty: {total - has_cover}')
if has_cover == total:
    print('ALL NOVELS NOW HAVE COVERS!')
