import os, sys, django, time, urllib.request
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

CAT_URLS = [
    '/dushixiaoshuo/', '/chuanyuexiaoshuo/', '/kehuanxiaoshuo/',
    '/wangyouxiaoshuo/', '/xuanyixiaoshuo/', '/wuxiaxiaoshuo/', '/lishixiaoshuo/',
]
CAT_IDS = ['3', '4', '6', '5', '1', '7', '2']

print('Phase 1: Building title->url mapping from category pages...\n')
title_map = {}

for cat_url, cat_id in zip(CAT_URLS, CAT_IDS):
    print(f'  Crawling {cat_url}...')
    for page in range(1, 6):
        list_url = f'{BASE}/fenlei/{cat_id}_{page}.html'
        try:
            r = session.get(list_url, timeout=15)
            html = etree.HTML(r.text)
            books = html.xpath("//div[@class='l']//a")
            if not books:
                break
            for a in books:
                href = a.get('href', '')
                title = ''.join(a.itertext()).strip()
                if title and href and not href.endswith('.html'):
                    full_url = BASE + href if not href.startswith('http') else href
                    title_map[title] = full_url
        except:
            break
        time.sleep(0.3)

print(f'\nCollected {len(title_map)} book URLs\n')

print('Phase 2: Downloading real covers...\n')

def get_cover_from_detail(detail_url):
    try:
        r = session.get(detail_url, timeout=15)
        r.encoding = 'utf-8'
        html = etree.HTML(r.text)
        imgs = html.xpath("//div[@id='fmimg']//img/@src")
        return imgs[0] if imgs else None
    except:
        return None

def dl_cover(nid, img_url):
    fname = f'cover_{nid:02d}.jpg'
    fpath = os.path.join(COVER_DIR, fname)
    if not img_url:
        return False, 'no_img'
    try:
        if not img_url.startswith('http'):
            img_url = BASE + img_url
        req = urllib.request.Request(img_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            if len(data) > 500:
                with open(fpath, 'wb') as f:
                    f.write(data)
                return True, len(data)
            return False, f'tiny({len(data)}B)'
    except Exception as e:
        return False, str(e)[:40]

novels = list(Novel.objects.filter(id__gte=88).order_by('id'))
ok = fail = no_url = no_img = miss = 0

for idx, novel in enumerate(novels):
    print(f'[{idx+1}/{len(novels)}] [{novel.id}] {novel.title[:28]}', end=' ')
    
    detail_url = title_map.get(novel.title)
    if not detail_url:
        print('MISS')
        miss += 1
        continue
    
    cover_url = get_cover_from_detail(detail_url)
    if not cover_url:
        print('NO_COVER')
        no_img += 1
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
print(f'Done! OK={ok}, NO_IMG={no_img}, FAIL={fail}, MISS={miss}')
