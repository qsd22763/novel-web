import os, sys, django, time
from urllib.parse import quote
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')
django.setup()
from novels.models import Novel
import requests

API = 'https://image.pollinations.ai/prompt/'
COVER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'covers')
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

CATEGORY_PROMPTS = {
    '都市': 'modern city life contemporary chinese urban drama neon lights',
    '穿越': 'time travel reincarnation ancient chinese palace historical fantasy',
    '科幻': 'sci-fi futuristic technology space cyberpunk chinese science fiction',
    '游戏': 'gaming RPG fantasy world level up adventure game interface',
    '悬疑': 'suspense mystery thriller dark atmosphere crime investigation',
    '武侠': 'wuxia martial arts chinese kung fu swordsman ancient mountains',
    '历史': 'historical dynasty ancient china emperor war strategy epic period drama',
    '玄幻': 'xianxia cultivation immortal fantasy chinese magical powers epic',
}

DEFAULT = 'chinese novel book cover dramatic cinematic digital art'

updated = 0
failed = 0
novels = Novel.objects.filter(id__gte=88).order_by('id')
total = novels.count()
print(f'Generating covers for {total} novels (id 88-165)...')

for idx, novel in enumerate(novels):
    fname = f'cover_{novel.id:02d}.jpg'
    fpath = os.path.join(COVER_DIR, fname)
    if os.path.exists(fpath) and os.path.getsize(fpath) > 5000:
        if novel.cover != f'/media/covers/{fname}':
            novel.cover = f'/media/covers/{fname}'
            novel.save(update_fields=['cover'])
        print(f'[{idx+1}/{total}] SKIP [{novel.id}] {novel.title[:20]}')
        continue

    cat_prompt = CATEGORY_PROMPTS.get(novel.category, DEFAULT)
    seed = (novel.id * 137 + hash(novel.title)) % (2**32)
    url = f'{API}{quote(cat_prompt)}?width=400&height=560&nologo=true&seed={seed}'

    ok = False
    for attempt in range(3):
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code == 200 and 'image' in resp.headers.get('Content-Type','') and len(resp.content) > 10000:
                with open(fpath, 'wb') as f:
                    f.write(resp.content)
                novel.cover = f'/media/covers/{fname}'
                novel.save(update_fields=['cover'])
                updated += 1
                ok = True
                print(f'[{idx+1}/{total}] OK [{novel.id}] {novel.title[:25]} ({len(resp.content)//1024}KB)')
                break
        except Exception as e:
            pass
        time.sleep(1)
    if not ok:
        failed += 1
        print(f'[{idx+1}/{total}] FAIL [{novel.id}] {novel.title[:25]}')
    time.sleep(0.3)

print(f'\nDone! {updated} generated, {failed} failed, out of {total} total.')
