"""
爬取小说封面：从起点中文网(qidian.com)按书名搜索并下载封面图片
"""
import os, sys, django, time, re, requests
from urllib.parse import quote

os.environ['DJANGO_SETTINGS_MODULE'] = 'novel_project.settings'
django.setup()
from novels.models import Novel

COVER_DIR = os.path.join('media', 'covers')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def search_qidian(title):
    """在起点搜索书籍，返回封面URL和书ID"""
    url = f'https://www.qidian.com/so/{quote(title)}.html'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None, None
        # 提取搜索结果中的书籍链接和封面
        # 模式1: bookcover img src
        cover_match = re.search(r'<img[^>]*class="[^"]*book-cover[^"]*"[^>]*src="(https?://[^"]+)"', resp.text)
        if cover_match:
            return cover_match.group(1), None
        # 模式2: 通用封面提取
        cover_match2 = re.search(r'(https?://[a-z0-9\-\.]+qidian[^"\'>\s]+(?:jpg|jpeg|png|webp))', resp.text)
        if cover_match2:
            return cover_match2.group(1), None
        return None, None
    except Exception as e:
        print(f'  [ERR] {title}: {e}')
        return None, None


def search_biquge(title):
    """备用：从笔趣阁等站点搜索封面"""
    urls_to_try = [
        f'https://www.bqg70.com/search.php?q={quote(title)}',
        f'https://www.xbiquge.so/search.php?q={quote(title)}',
    ]
    for url in urls_to_try:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code != 200:
                continue
            match = re.search(r'<img[^>]*src="([^"]*(?:cover|img|pic)[^"]*\.(?:jpg|jpeg|png))"', resp.text, re.I)
            if match:
                return match.group(1)
        except:
            continue
    return None


def download_cover(url, save_path):
    """下载封面图片"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, stream=True)
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

            # 验证文件大小（至少1KB）
            if os.path.getsize(final_path) > 1024:
                return final_path
            else:
                os.remove(final_path)
                return None
    except Exception as e:
        print(f'  [DL ERR] {e}')
    return None


def main():
    no_cover = list(Novel.objects.filter(cover='') | Novel.objects.filter(cover__isnull=True))
    print(f'Total novels without cover: {len(no_cover)}')
    print('=' * 60)

    success = 0
    failed = []

    for i, novel in enumerate(no_cover, 1):
        title = novel.title
        print(f'\n[{i}/{len(no_cover)}] {title} ...', end=' ')

        # Strategy 1: Qidian search
        cover_url, _ = search_qidian(title)

        # Strategy 2: Biquge fallback
        if not cover_url:
            cover_url = search_biquge(title)

        if not cover_url:
            print('NOT FOUND')
            failed.append(title)
            time.sleep(0.3)
            continue

        # Download
        safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)[:50]
        save_base = os.path.join(COVER_DIR, safe_title)
        result_path = download_cover(cover_url, save_base)

        if result_path:
            fname = os.path.basename(result_path)
            novel.cover = '/media/covers/' + fname
            novel.save(update_fields=['cover'])
            success += 1
            print(f'OK -> {fname}')
        else:
            print('DOWNLOAD FAILED')
            failed.append(title)

        time.sleep(0.5)  # 礼貌间隔

    print('\n' + '=' * 60)
    print(f'Done! Success: {success}, Failed: {len(failed)}, Total: {len(no_cover)}')
    if failed:
        print(f'\nFailed titles ({len(failed)}):')
        for f in failed:
            print(f'  - {f}')


if __name__ == '__main__':
    main()
