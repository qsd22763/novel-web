import os, sys, django, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')
django.setup()

from PIL import Image, ImageDraw, ImageFont
from novels.models import Novel

W, H = 400, 560
COVER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'covers')
os.makedirs(COVER_DIR, exist_ok=True)

PALETTES = {
    '玄幻': [(45, 25, 60), (120, 40, 100), (180, 60, 140)],
    '都市': [(20, 35, 60), (50, 80, 130), (90, 120, 180)],
    '穿越': [(60, 30, 20), (140, 70, 40), (200, 110, 60)],
    '科幻': [(10, 25, 45), (25, 55, 95), (45, 85, 140)],
    '游戏': [(15, 40, 30), (30, 90, 60), (50, 140, 90)],
    '悬疑': [(30, 28, 35), (65, 55, 70), (100, 85, 105)],
    '武侠': [(50, 35, 20), (110, 75, 40), (170, 115, 60)],
    '历史': [(55, 38, 22), (120, 82, 42), (180, 125, 62)],
}

def try_font(size, bold=False):
    fonts = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for f in fonts:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()

def make_gradient(draw, w, h, colors):
    for y in range(h):
        r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * y / h)
        g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * y / h)
        b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

def add_decorations(draw, w, h, palette):
    c2 = tuple(palette[2])
    for i in range(0, w + h, 40):
        x = min(i, w)
        y = max(0, i - w)
        alpha = random.randint(15, 35)
        draw.rectangle([x, y, x + 8, y + 8], fill=(*c2[:3], alpha))
    draw.rectangle([16, 16, w - 17, h - 17], outline=(*c2[:3], 80), width=1)

def wrap_text(text, font, max_width):
    lines = []
    for ch in text:
        test = (lines[-1] + ch) if lines else ch
        bbox = font.getbbox(test)
        if bbox[2] - bbox[0] <= max_width:
            if lines: lines[-1] = test
            else: lines.append(test)
        else:
            lines.append(ch)
    return lines

updated = 0
for novel in Novel.objects.all().order_by('id'):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    
    palette = PALETTES.get(novel.category, PALETTES['玄幻'])
    make_gradient(draw, W, H, palette)
    add_decorations(draw, W, H, palette)
    
    title_font = try_font(36, bold=True)
    author_font = try_font(18)
    cat_font = try_font(14)
    
    title_lines = wrap_text(novel.title, title_font, W - 60)
    ty = H // 2 - len(title_lines) * 24
    for line in title_lines:
        bbox = title_font.getbbox(line)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, ty), line, fill=(255, 245, 220, 255), font=title_font)
        ty += 44
    
    draw.line([(40, ty + 8), (W - 40, ty + 8)], fill=(200, 170, 100, 180), width=1)
    
    author_bbox = author_font.getbbox(novel.author)
    aw = author_bbox[2] - author_bbox[0]
    draw.text(((W - aw) // 2, ty + 18), novel.author, fill=(200, 190, 170, 220), font=author_font)
    
    cat_text = f'「{novel.category}」'
    cat_bbox = cat_font.getbbox(cat_text)
    cw = cat_bbox[2] - cat_bbox[0]
    draw.text(((W - cw) // 2, H - 48), cat_text, fill=(180, 150, 100, 180), font=cat_font)
    
    fname = f'cover_{novel.id:02d}.jpg'
    fpath = os.path.join(COVER_DIR, fname)
    rgb = Image.new('RGB', img.size, (255, 255, 255))
    rgb.paste(img, mask=img.split()[-1])
    rgb.save(fpath, 'JPEG', quality=92)
    
    novel.cover = f'/media/covers/{fname}'
    novel.save(update_fields=['cover'])
    updated += 1
    print(f'  OK [{novel.id}] {novel.title} ({novel.category})')

print(f'\nDone! {updated}/{Novel.objects.count()} covers generated.')
