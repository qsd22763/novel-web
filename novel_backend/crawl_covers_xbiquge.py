"""
从 xbiquge.la 笔趣阁详情页爬取小说封面图片
流程：搜索书名 → 进入详情页 → 提取封面 → 下载保存 → 更新数据库
规则：仅使用真实爬取原图，匹配不到则留空，不使用通用占位图
"""
import os, sys, django, time, re, requests
from urllib.parse import quote, urljoin

os.environ['DJANGO_SETTINGS_MODULE'] = 'novel_project.settings'
django.setup()
from novels.models import Novel

COVER_DIR = os.path.join('media', 'covers')
os.makedirs(COVER_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.xbiquge.la/',
}

BASE_URL = 'https://www.xbiquge.la'


def search_xbiquge(title):
    """在 xbiquge.la 搜索书籍，返回(详情页路径, 书名)列表"""
    url = f'{BASE_URL}/modules/article/waps.php?searchkey={quote(title)}'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return []

        # 搜索结果中的书籍链接格式:
        # <td><a href="/7/7877/" target="_blank">斗 破苍穹</a></td>
        # 或 <a href="http://www.xbiqugu.la/7/7877/">书名</a>
        links = re.findall(
            r'<a\s+href="(?:http://www\.xbiqugu\.la)?(/[\d]+/[\d]+/)"[^>]*target="_blank"\s*>([^<]+)</a>',
            resp.text
        )
        result_urls = []
        for href, name in links[:5]:
            result_urls.append((href, name.strip()))
        return result_urls
    except Exception as e:
        print(f'  [搜索失败] {e}')
        return []


def extract_cover_from_detail(path):
    """从 xbiquge.la 详情页提取封面图片URL"""
    detail_url = f'{BASE_URL}{path}'
    try:
        headers = dict(HEADERS)
        headers['Referer'] = detail_url
        resp = requests.get(detail_url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return None

        # 模式1: 封面图片路径特征 files/article/image/...
        match = re.search(r'src="(https?://[^"]*(?:files/article/image|cover)[^"]+\.(?:jpg|jpeg|png|webp))"', resp.text)
        if match:
            return match.group(1)

        # 模式2: .fm div 内的img标签（详情页左侧封面区）
        match2 = re.search(r'<div\s+class="fm"[^>]*>.*?<img\s+src="([^"]+)"', resp.text, re.S)
        if match2:
            u = match2.group(1)
            if not u.startswith('http'):
                u = urljoin(detail_url, u)
            return u

        # 模式3: 页面中所有img，排除广告/图标等小图
        imgs = re.findall(r'<img[^>]*src="([^"]+)"', resp.text)
        for img_url in imgs:
            # 排除明显的非封面图
            if any(skip in img_url.lower() for skip in ['baidu', 'google', 'analytics', 'icon', 'logo', 'button', 'type-button']):
                continue
            # 封面图通常包含 image/ 或 cover 或 book 关键词
            if any(kw in img_url.lower() for kw in ['image/', '/files/', 'article/image', 'cover']):
                if not img_url.startswith('http'):
                    img_url = urljoin(detail_url, img_url)
                return img_url

        return None
    except Exception as e:
        print(f'  [详情页解析失败] {e}')
        return None


def download_cover(cover_url, save_path):
    """下载封面图片并返回实际保存路径"""
    try:
        headers = dict(HEADERS)
        parsed = requests.utils.urlparse(cover_url)
        headers['Referer'] = f'{parsed.scheme}://{parsed.netloc}/'

        resp = requests.get(cover_url, headers=headers, timeout=20, stream=True)
        if resp.status_code == 200:
            content_type = resp.headers.get('Content-Type', '')
            ext = '.jpg'
            if 'png' in content_type:
                ext = '.png'
            elif 'webp' in content_type:
                ext = '.webp'

            final_path = save_path + ext
            with open(final_path, 'wb') as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)

            size = os.path.getsize(final_path)
            if size > 2048:
                return final_path
            else:
                os.remove(final_path)
                print(f'  [文件过小 {size}B]')
                return None
    except Exception as e:
        print(f'  [下载失败] {e}')
    return None


def process_novel(novel):
    """处理单本小说：搜索→详情页→提取封面→下载→入库"""
    title = novel.title

    # Step 1: 搜索
    results = search_xbiquge(title)
    if not results:
        return False, '搜索无结果'

    # Step 2: 遍历搜索结果，进入每个详情页提取封面
    for detail_path, result_name in results:
        cover_url = extract_cover_from_detail(detail_path)
        if not cover_url:
            continue

        # Step 3: 下载
        safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)[:50]
        save_base = os.path.join(COVER_DIR, safe_title)
        result_path = download_cover(cover_url, save_base)

        if result_path:
            fname = os.path.basename(result_path)
            db_path = '/media/covers/' + fname
            novel.cover = db_path
            novel.save(update_fields=['cover'])
            return True, fname

    return False, '所有结果均未找到封面'


def main():
    no_cover = list(Novel.objects.filter(cover='') | Novel.objects.filter(cover__isnull=True))
    print(f'=== 待爬取封面小说共 {len(no_cover)} 本 ===\n')

    success = 0
    failed_list = []

    for i, novel in enumerate(no_cover, 1):
        title = novel.title
        cat = novel.category
        print(f'[{i}/{len(no_cover)}] [{cat}] {title}', end=' ... ')

        ok, msg = process_novel(novel)
        if ok:
            success += 1
            print(f'OK -> {msg}')
        else:
            failed_list.append(title)
            print(f'FAIL ({msg})')

        time.sleep(0.6)

    print('\n' + '=' * 60)
    print(f'Done! Success: {success}, Failed: {len(failed_list)}, Total: {len(no_cover)}')
    if failed_list:
        print(f'\nFailed titles ({len(failed_list)}):')
        for t in failed_list:
            print(f'  - {t}')

    remaining = Novel.objects.filter(cover='') | Novel.objects.filter(cover__isnull=True)
    print(f'\nRemaining no-cover books: {remaining.count()}')


if __name__ == '__main__':
    main()
