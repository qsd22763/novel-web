import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'novel_project.settings'
django.setup()
from novels.models import Novel

cover_dir = 'media/covers'
files = [f for f in os.listdir(cover_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
named_files = [os.path.splitext(f)[0] for f in files if not f.startswith('cover_')]

novels = list(Novel.objects.values_list('id', 'title', 'cover'))
no_cover = [n for n in novels if not n[2]]

print(f'=== Novels WITHOUT cover ({len(no_cover)}) ===')
for nid, title, _ in no_cover:
    print(f'  [{title}]')

print(f'\n=== Named cover files ({len(named_files)}) ===')
for nf in sorted(named_files)[:40]:
    print(f'  {nf}')
