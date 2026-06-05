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

remaining = list(Novel.objects.all().order_by('id'))
print(f'Processing {len(remaining)} novels...\n')

title_map = {}
for cat_id in ['1','2','3','4','5','6','7']:
    for page in range(1, 21):
        url = f'{BASE}/fenlei/{cat_id}_{page}.html'
        try:
            r = session.get(url, timeout=12)
            html = etree.HTML(r.text)
            for a in html.xpath("//div[@class='l']//a"):
                href = a.get('href', '')
                title = ''.join(a.itertext()).strip()
                if title and href and not href.endswith('.html'):
                    full_url = BASE + href if not href.startswith('http') else href
                    title_map[title] = full_url
        except:
            break
        time.sleep(0.15)

print(f'Mapped {len(title_map)} titles\n')

def get_cover(detail_url):
    try:
        r = session.get(detail_url, timeout=12)
        r.encoding = 'utf-8'
        imgs = etree.HTML(r.text).xpath("//div[@id='fmimg']//img/@src")
        return imgs[0] if imgs else None
    except: return None

def dl(nid, img_url):
    fpath = os.path.join(COVER_DIR, f'cover_{nid:02d}.jpg')
    if not img_url: return False, 'no_img'
    try:
        u = img_url if img_url.startswith('http') else BASE + img_url
        req = urllib.request.Request(u, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = resp.read()
            if len(data) > 500:
                with open(fpath, 'wb') as f: f.write(data)
                return True, len(data)
            return False, 'tiny'
    except Exception as e: return False, str(e)[:30]

for novel in remaining:
    print(f'[{novel.id}] {novel.title}', end=' -> ')
    
    best_match = None
    best_score = 0
    for t, u in title_map.items():
        score = sum(1 for c in novel.title if c in t)
        if score > best_score:
            best_score = score
            best_match = (t, u)
    
    if best_match and best_score >= 4:
        print(f'Match: "{best_match[0][:30]}"', end=' ... ')
        cu = get_cover(best_match[1])
        if cu:
            s, r = dl(novel.id, cu)
            if s:
                novel.cover = f'/media/covers/cover_{novel.id:02d}.jpg'
                novel.save(update_fields=['cover'])
                print(f'OK ({r//1024}KB)')
            else: print(f'DL_FAIL({r})')
        else: print('NO_COVER')
    else:
        print(f'NO_MATCH (best={best_score})')
    time.sleep(0.3)
