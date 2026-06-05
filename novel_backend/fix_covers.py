import os, sys, django, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')
django.setup()
from novels.models import Novel
from lxml import etree
import requests

BASE = 'https://www.xbiquge.la'
COVER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'covers')

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
session = requests.Session()
session.headers.update(HEADERS)
for k in ['HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy','ALL_PROXY','all_proxy']:
    os.environ[k] = ''
session.trust_env = False

print('Phase 1: Building title->url map...\n')
title_map = {}
for cat_id in ['1','2','3','4','5','6','7']:
    for page in range(1, 16):
        try:
            r = session.get(f'{BASE}/fenlei/{cat_id}_{page}.html', timeout=12)
            html = etree.HTML(r.text)
            for a in html.xpath("//div[@class='l']//a"):
                href = a.get('href', '')
                title = ''.join(a.itertext()).strip()
                if title and href and not href.endswith('.html'):
                    full_url = BASE + href if not href.startswith('http') else href
                    if title not in title_map:
                        title_map[title] = full_url
        except: break
        time.sleep(0.2)
print(f'Mapped {len(title_map)} titles\n')

def get_cover_url(detail_url):
    try:
        r = session.get(detail_url, timeout=12)
        r.encoding = 'utf-8'
        imgs = etree.HTML(r.text).xpath("//div[@id='fmimg']//img/@src")
        return imgs[0] if imgs else None
    except: return None

def dl_cover(nid, img_url):
    fpath = os.path.join(COVER_DIR, f'cover_{nid:02d}.jpg')
    if not img_url: return False, 'no_img'
    try:
        url = img_url if img_url.startswith('http') else BASE + img_url
        r = session.get(url, timeout=15)
        ct = r.headers.get('Content-Type', '')
        if 'image' not in ct and len(r.content) < 10000:
            return False, f'not_image({ct})'
        if len(r.content) > 500:
            with open(fpath, 'wb') as f: f.write(r.content)
            return True, len(r.content)
        return False, f'tiny({len(r.content)}B)'
    except Exception as e: return False, str(e)[:35]

novels = list(Novel.objects.filter(id__gte=88).order_by('id'))
ok = fail = miss = 0

for idx, novel in enumerate(novels):
    print(f'[{idx+1}/{len(novels)}] [{novel.id}] {novel.title[:28]}', end=' ... ')
    
    detail_url = title_map.get(novel.title)
    if not detail_url:
        print('MISS')
        miss += 1
        continue
    
    cover_url = get_cover_url(detail_url)
    if not cover_url:
        print('NO_COVER_ON_PAGE')
        fail += 1
        continue
    
    success, result = dl_cover(novel.id, cover_url)
    if success:
        novel.cover = f'/media/covers/cover_{novel.id:02d}.jpg'
        novel.save(update_fields=['cover'])
        ok += 1
        print(f'OK ({result//1024}KB)')
    else:
        fail += 1
        print(f'FAIL({result})')
    time.sleep(0.3)

print(f'\n{"="*50}')
print(f'Done! OK={ok}, FAIL={fail}, MISS={miss}')
