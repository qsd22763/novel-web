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

broken_ids = [91,92,95,113,115,119,120]
broken = list(Novel.objects.filter(id__in=broken_ids).order_by('id'))
print(f'Fixing {len(broken)} broken covers with deep search...\n')

title_map = {}
for cat_id in ['1','2','3','4','5','6','7']:
    for page in range(1, 31):
        try:
            r = session.get(f'{BASE}/fenlei/{cat_id}_{page}.html', timeout=10)
            html = etree.HTML(r.text)
            for a in html.xpath("//div[@class='l']//a"):
                href = a.get('href', '')
                title = ''.join(a.itertext()).strip()
                if title and href and not href.endswith('.html'):
                    full_url = BASE + href if not href.startswith('http') else href
                    if title not in title_map:
                        title_map[title] = full_url
        except: break
        time.sleep(0.15)

print(f'Mapped {len(title_map)} titles\n')

def get_cover(detail_url):
    try:
        r = session.get(detail_url, timeout=12)
        r.encoding = 'utf-8'
        return etree.HTML(r.text).xpath("//div[@id='fmimg']//img/@src")
    except: return []

def dl(nid, img_url):
    fpath = os.path.join(COVER_DIR, f'cover_{nid:02d}.jpg')
    if not img_url: return False, 'no_img'
    try:
        u = img_url if img_url.startswith('http') else BASE + img_url
        r = session.get(u, timeout=15)
        if len(r.content) > 500:
            with open(fpath, 'wb') as f: f.write(r.content)
            return True, len(r.content)
        return False, 'tiny'
    except Exception as e: return False, str(e)[:30]

ok = 0
for novel in broken:
    print(f'[{novel.id}] {novel.title[:30]}', end=' -> ')
    
    url = title_map.get(novel.title)
    if not url:
        print('STILL_MISS')
        continue
    
    imgs = get_cover(url)
    if not imgs:
        print('NO_COVER')
        continue
    
    s, r = dl(novel.id, imgs[0])
    if s:
        novel.cover = f'/media/covers/cover_{novel.id:02d}.jpg'
        novel.save(update_fields=['cover'])
        ok += 1
        print(f'OK ({r//1024}KB)')
    else:
        print(f'FAIL({r})')
    time.sleep(0.3)

print(f'\nFixed: {ok}/{len(broken)}')
