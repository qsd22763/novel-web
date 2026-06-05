import os, sys, django, time
from urllib.parse import quote
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')
django.setup()
from novels.models import Novel
import requests

API = 'https://image.pollinations.ai/prompt/'
COVER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'covers')

PROMPTS = {
    '序列：吃神者': 'dark fantasy horror novel cover eerie shadows glowing eyes supernatural thriller',
    '第19次末日': 'post-apocalyptic wasteland ruins survival novel cover dramatic sky',
    '宇智波赤石之旅': 'anime ninja action manga style sharingan eye red chakra fire',
    '游戏入侵：我一路杀到诸神颤抖': 'gaming RPG fantasy warrior god slayer epic lightning sword',
}
DEFAULT = 'epic chinese novel book cover dramatic cinematic digital art'

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})
for k in ['HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy','ALL_PROXY','all_proxy']:
    os.environ[k] = ''

for nid in [113, 115, 119, 120]:
    novel = Novel.objects.get(id=nid)
    fname = f'cover_{nid:02d}.jpg'
    fpath = os.path.join(COVER_DIR, fname)
    
    prompt = PROMPTS.get(novel.title, DEFAULT)
    seed = (nid * 137 + hash(novel.title)) % (2**32)
    url = f'{API}{quote(prompt)}?width=400&height=560&nologo=true&seed={seed}'
    
    print(f'[{nid}] {novel.title[:25]} ... ', end='')
    ok = False
    for attempt in range(3):
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open(fpath, 'wb') as f: f.write(resp.content)
                novel.cover = f'/media/covers/{fname}'
                novel.save(update_fields=['cover'])
                print(f'AI OK ({len(resp.content)//1024}KB)')
                ok = True
                break
        except: pass
        time.sleep(1)
    if not ok:
        print('FAIL')
    time.sleep(0.5)

print('\nDone! AI fallback covers generated.')
