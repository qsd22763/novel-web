#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
墨香书阁 — 高清封面爬取脚本 v2
数据源：
  - 主源: xbiqugu.la 分类列表（笔趣阁系站点）
  - 备源: 必应图片搜索（主源未命中时自动切换）

功能：
  1. 预建站点索引，批量匹配数据库书籍
  2. 解析详情页提取封面，过滤缩略图（<300px拒绝）
  3. 自动清空 media/covers/ 全量重新拉取
  4. 主源未找到时自动尝试图片搜索引擎
  5. 下载完成后更新数据库 cover 字段

用法：python crawl_covers_xbiquge.py [--dry-run] [--book-id ID] [--no-clear]
"""

import os
import sys
import time
import re
import json
import hashlib
import logging
import random
from datetime import datetime
from typing import Optional, Tuple, List, Dict
from io import BytesIO
from urllib.parse import quote

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Django 环境初始化
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')

import django
django.setup()

from novels.models import Novel

import requests
from lxml import etree

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger('CoverCrawler')

# ============================================================
# 配置
# ============================================================
BASE_URL = 'http://www.xbiqugu.la'
COVER_DIR = os.path.join(BASE_DIR, 'media', 'covers')
MIN_WIDTH = 300
MIN_HEIGHT = 400

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': BASE_URL + '/',
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# 站点分类ID（fenlei参数）
SITE_CATEGORIES = [1, 2, 3, 4, 5, 6, 7]  # 玄幻/修真/都市/穿越/网游/科幻/其他
MAX_INDEX_PAGES = 25  # 每类最多索引页数


def clean_filename(title: str) -> str:
    title = re.sub(r'[\\/:*?"<>|]', '', title).strip()
    return title[:50] if len(title) > 50 else title


def get_image_size(data: bytes) -> Optional[Tuple[int, int]]:
    if not HAS_PIL:
        return None
    try:
        img = Image.open(BytesIO(data))
        return img.size
    except Exception:
        return None


def is_valid_cover(data: bytes, url: str = '') -> Tuple[bool, str, Optional[Tuple[int, int]]]:
    if not data or len(data) < 2000:
        return False, '数据过小(<2KB)', None
    if len(data) < 5000:
        return False, f'文件仅{len(data)}B，疑似占位图', None

    size = get_image_size(data)
    if size is None:
        if len(data) > 20000:
            return True, '无法解析尺寸但数据量充足(>20KB)', None
        return False, '无法解析图片尺寸且数据量不足', None

    w, h = size
    if w < MIN_WIDTH or h < MIN_HEIGHT:
        return False, f'尺寸太小 {w}x{h} < {MIN_WIDTH}x{MIN_HEIGHT}', size

    ratio = w / h if h > 0 else 0
    if ratio > 5 or ratio < 0.15:
        return False, f'宽高比异常 {ratio:.2f} ({w}x{h})', size

    return True, f'通过校验 {w}x{h}', size


def fetch_page(url: str, retries: int = 3) -> Optional[str]:
    for attempt in range(retries):
        try:
            resp = SESSION.get(url, timeout=20)
            resp.encoding = resp.apparent_encoding or 'gbk'
            if resp.status_code == 200:
                return resp.text
            log.warning(f"  HTTP {resp.status_code}: {url}")
            time.sleep(2 ** attempt)
        except Exception as e:
            log.warning(f"  请求失败(第{attempt+1}次): {e}")
            time.sleep(2)
    return None


def download_image(url: str, timeout: int = 30, referer: str = '') -> Optional[bytes]:
    try:
        headers = dict(HEADERS)
        if referer:
            headers['Referer'] = referer
        else:
            headers['Referer'] = BASE_URL + '/'
        resp = SESSION.get(url, headers=headers, timeout=timeout, stream=True)
        if resp.status_code == 200:
            return resp.content
    except Exception as e:
        log.debug(f"  下载失败 [{url[:60]}]: {e}")
    return None


def save_cover(data: bytes, title: str) -> Optional[str]:
    ext = 'jpg'
    if len(data) >= 4:
        if data[:4] == b'\x89PNG':
            ext = 'png'
        elif data[:4] == b'RIFF':
            ext = 'webp'

    fname = f"{clean_filename(title)}.{ext}"
    fpath = os.path.join(COVER_DIR, fname)

    counter = 1
    while os.path.exists(fpath):
        fname = f"{clean_filename(title)}_{counter}.{ext}"
        fpath = os.path.join(COVER_DIR, fname)
        counter += 1

    try:
        with open(fpath, 'wb') as f:
            f.write(data)
        rel_path = f'/media/covers/{fname}'
        log.info(f"  已保存: {fname} ({len(data)//1024}KB)")
        return rel_path
    except Exception as e:
        log.error(f"  保存失败: {e}")
        return None


# ============================================================
# 1. 站点索引构建
# ============================================================

def build_site_index() -> Dict[str, Tuple[str, int, int]]:
    """
    预遍历 xbiqugu.la 所有分类列表页，构建书名->详情URL映射
    返回: {title: (detail_url, cat_id, page)}
    """
    log.info("正在构建站点书籍索引...")
    index = {}
    total_books = 0

    for cat_id in SITE_CATEGORIES:
        for page in range(1, MAX_INDEX_PAGES + 1):
            url = f'{BASE_URL}/fenlei/{cat_id}_{page}.html'
            html = fetch_page(url)
            if not html:
                break

            tree = etree.HTML(html)
            items = tree.xpath("//span[@class='s2']/a")
            if not items:
                break  # 无数据，到达末页

            for item in items:
                title = ''.join(item.xpath('.//text()')).strip()
                href = item.get('href', '')
                if title and href and title not in index:
                    full_url = href if href.startswith('http') else BASE_URL + href
                    index[title] = (full_url, cat_id, page)
                    total_books += 1

            # 每页间稍作延迟
            time.sleep(0.3)

        log.info(f"  分类{cat_id}索引完成")

    log.info(f"索引构建完毕: {total_books} 本书, {len(index)} 个唯一书名")
    return index


# ============================================================
# 2. 书名匹配
# ============================================================

def match_novel(title: str, index: Dict[str, Tuple[str, int, int]]) -> Optional[Tuple[str, str]]:
    """
    在索引中匹配小说，返回 (detail_url, match_type)
    match_type: 'exact' | 'fuzzy'
    """
    # 精确匹配
    if title in index:
        url, cat_id, page = index[title]
        return url, 'exact'

    # 包含匹配：站名包含DB名 或 DB名包含站名
    best_match = None
    best_len = 0

    for site_title, (url, cat_id, page) in index.items():
        if title in site_title or site_title in title:
            # 取较长匹配长度
            match_len = max(
                len(title) if title in site_title else 0,
                len(site_title) if site_title in title else 0
            )
            if match_len > best_len:
                best_len = match_len
                best_match = (url, 'fuzzy')

    return best_match


# ============================================================
# 3. 从详情页提取高清封面
# ============================================================

def extract_cover_from_detail(detail_html: str, detail_url: str) -> Optional[str]:
    """从详情页HTML提取并验证最佳封面URL"""
    tree = etree.HTML(detail_html)
    candidates = []

    # 策略1: #fmimg 主封面
    for img in tree.xpath("//div[@id='fmimg']//img"):
        src = img.get('src') or img.get('data-src') or ''
        if src:
            if not src.startswith('http'):
                src = BASE_URL + src
            candidates.append((src, 'fmimg'))

    # 策略2: OG meta
    for attr in ["@property='og:image'", "@name='twitter:image'"]:
        for src in tree.xpath(f'//meta[{attr}]/@content'):
            if src and src.startswith('http'):
                candidates.append((src.strip(), 'OG meta'))

    # 去重
    seen = set()
    unique = []
    for url, desc in candidates:
        key = url.split('?')[0].rstrip('/')
        if key not in seen:
            seen.add(key)
            unique.append((url, desc))

    if not unique:
        log.warning("  详情页未找到任何候选封面")
        return None

    # 逐一下载验证
    best_url = None
    best_score = -1

    for url, source in unique:
        data = download_image(url)
        if not data:
            continue

        valid, reason, size = is_valid_cover(data, url)
        if valid:
            score = (size[0] * size[1]) if size else (len(data) * 10)
            if 'fmimg' in source:
                score += 50000
            elif 'og' in source.lower():
                score += 30000
            log.info(f"  候选[{source}]: {reason} score={score}")
            if score > best_score:
                best_score = score
                best_url = url
        else:
            log.info(f"  候选[{source}]: 跳过 - {reason}")

    if best_url:
        log.info(f"  最佳封面: {best_url[:80]}... (score={best_score})")
    else:
        log.warning("  所有候选均未通过校验")

    return best_url


# ============================================================
# 4. 备选：必应图片搜索
# ============================================================

def search_bing_image(title: str) -> Optional[str]:
    """
    通过必应图片搜索获取封面
    返回最佳图片URL或None
    """
    log.info(f"  [备选] 尝试必应图片搜索: {title}")
    search_url = f'https://cn.bing.com/images/search?q={quote(title + " 小说封面")}&first=1&count=10&qft=+filterui:photo-large'

    try:
        html = fetch_page(search_url)
        if not html:
            return None

        tree = etree.HTML(html)
        # 必应图片搜索结果中的缩略图链接
        mlinks = tree.xpath("//a[contains(@class,'iusc')]/@m")
        if not mlinks:
            # 备选XPath
            mlinks = tree.xpath("//div[@class='imgpt']//a/@m | //div[contains(@class,'imgarea')]//a/@m")

        best_url = None
        best_score = -1

        for mdata in mlinks[:15]:
            try:
                info = json.loads(mdata)
                img_url = info.get('murl', '')
                if not img_url:
                    continue

                data = download_image(img_url, timeout=15, referer='https://cn.bing.com/')
                if not data:
                    continue

                valid, reason, size = is_valid_cover(data, img_url)
                if valid:
                    score = (size[0] * size[1]) if size else (len(data) * 10)
                    if score > best_score:
                        best_score = score
                        best_url = img_url
                        log.info(f"  必应候选: {reason} score={score}")
            except (json.JSONDecodeError, KeyError):
                continue
            except Exception:
                continue

        if best_url:
            log.info(f"  必应最佳: {best_url[:80]}...")
        return best_url

    except Exception as e:
        log.warning(f"  必应搜索异常: {e}")
        return None


# ============================================================
# 5. 处理单本小说
# ============================================================

def process_novel(novel: Novel, index: Dict[str, Tuple[str, int, int]],
                  dry_run: bool = False) -> Tuple[bool, str]:
    """
    处理单本小说的封面下载
    返回: (success, source)  source='site'|'bing'|'none'
    """
    title = novel.title
    log.info(f"\n{'='*50}")
    log.info(f"[{novel.id}] {title}")

    # ── Step 1: 站点索引匹配 ──
    match_result = match_novel(title, index)
    detail_url = None
    source = 'none'

    if match_result:
        detail_url, match_type = match_result
        log.info(f"  站点匹配({match_type}): {detail_url}")

        # 获取详情页
        detail_html = fetch_page(detail_url)
        if detail_html:
            cover_url = extract_cover_from_detail(detail_html, detail_url)
            if cover_url:
                if dry_run:
                    log.info(f"  [DRY-RUN] 站点封面: {cover_url}")
                    return True, 'site'

                data = download_image(cover_url)
                if data:
                    valid, reason, size = is_valid_cover(data, cover_url)
                    if not valid:
                        log.warning(f"  站点封面校验失败: {reason}, 切换备选...")
                    else:
                        rel_path = save_cover(data, title)
                        if rel_path:
                            novel.cover = rel_path
                            novel.save(update_fields=['cover'])
                            return True, 'site'

    # ── Step 2: 备选 — 必应图片搜索 ──
    log.info("  站点无可用封面，尝试备选方案...")
    bing_url = search_bing_image(title)

    if bing_url:
        if dry_run:
            log.info(f"  [DRY-RUN] 必应封面: {bing_url}")
            return True, 'bing'

        data = download_image(bing_url, referer='https://cn.bing.com/')
        if data:
            valid, reason, size = is_valid_cover(data, bing_url)
            if not valid:
                log.error(f"  必应封面校验也失败: {reason}")
            else:
                rel_path = save_cover(data, title)
                if rel_path:
                    novel.cover = rel_path
                    novel.save(update_fields=['cover'])
                    return True, 'bing'

    # ── 全部失败 ──
    log.error(f"  未找到任何可用封面")
    return False, 'none'


def clear_covers_dir():
    if os.path.exists(COVER_DIR):
        count = 0
        for f in os.listdir(COVER_DIR):
            fpath = os.path.join(COVER_DIR, f)
            if os.path.isfile(fpath):
                os.remove(fpath)
                count += 1
        log.info(f"已清空 {COVER_DIR} ({count} 个文件)")
    else:
        os.makedirs(COVER_DIR, exist_ok=True)
        log.info(f"创建目录 {COVER_DIR}")


# ============================================================
# 主流程
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description='墨香书阁高清封面爬取工具')
    parser.add_argument('--dry-run', action='store_true', help='试运行不实际下载')
    parser.add_argument('--book-id', type=int, default=None, help='只处理指定ID')
    parser.add_argument('--no-clear', action='store_true', help='不清空旧封面')
    args = parser.parse_args()

    start_time = time.time()

    log.info("=" * 55)
    log.info("墨香书阁 - 高清封面爬取工具 v2")
    log.info(f"Pillow: {'是' if HAS_PIL else '否'}")
    log.info(f"主源: {BASE_URL}  |  备源: 必应图片搜索")
    log.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 55)

    # 清空旧封面
    if not args.no_clear and not args.dry_run:
        clear_covers_dir()
    elif args.no_clear:
        log.info("跳过清空 (--no-clear)")

    # 查询小说
    qs = Novel.objects.all()
    if args.book_id:
        qs = qs.filter(id=args.book_id)
        log.info(f"仅处理 ID={args.book_id}")

    total = qs.count()
    log.info(f"共 {total} 本小说\n")

    # 预建索引
    index = build_site_index()
    log.info("")

    # 统计
    stats = {'site': 0, 'bing': 0, 'fail': 0}
    failed_titles = []

    for i, novel in enumerate(qs, 1):
        log.info(f"[{i}/{total}] ", extra={'extra': ''})
        try:
            ok, src = process_novel(novel, index, dry_run=args.dry_run)
            if ok:
                stats[src] = stats.get(src, 0) + 1
            else:
                stats['fail'] += 1
                failed_titles.append(novel.title)
        except KeyboardInterrupt:
            log.warning("\n用户中断")
            break
        except Exception as e:
            log.error(f"  异常: {e}")
            stats['fail'] += 1
            failed_titles.append(novel.title)

        time.sleep(0.5 + random.uniform(0.3, 0.8))

    # 汇总
    elapsed = time.time() - start_time
    log.info(f"\n{'='*55}")
    log.info(f"完成! 耗时 {elapsed:.1f}s")
    log.info(f"站点源: {stats.get('site', 0)} | 必应备源: {stats.get('bing', 0)} | 失败: {stats['fail']}")
    log.info(f"总计: {total} | 成功率: {(stats.get('site',0)+stats.get('bing',0))/max(total,1)*100:.1f}%")
    if failed_titles:
        log.info(f"未找到封面的书籍 ({len(failed_titles)}本):")
        for t in failed_titles:
            log.info(f"  - {t}")
    log.info(f"封面目录: {COVER_DIR}")
    log.info("=" * 55)


if __name__ == '__main__':
    main()
