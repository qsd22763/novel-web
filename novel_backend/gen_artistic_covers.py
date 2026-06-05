import os, sys, django, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')
django.setup()

from PIL import Image, ImageDraw, ImageFilter
from novels.models import Novel

W, H = 400, 560
COVER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'covers')
os.makedirs(COVER_DIR, exist_ok=True)

def try_font(size, bold=False):
    fonts = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    for f in fonts:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()

from PIL import ImageFont

THEMES = {
    '玄幻': {
        'bg': [(30, 12, 50), (80, 30, 100), (140, 50, 160)],
        'accent': (255, 200, 80),
        'glow': (180, 100, 255),
        'elements': ['flame', 'dragon', 'mountain', 'star'],
        'mood': 'mystical',
    },
    '都市': {
        'bg': [(15, 25, 50), (40, 60, 110), (70, 100, 170)],
        'accent': (100, 200, 255),
        'glow': (150, 180, 255),
        'elements': ['city', 'building', 'light'],
        'mood': 'modern',
    },
    '穿越': {
        'bg': [(55, 25, 15), (130, 65, 35), (200, 100, 55)],
        'accent': (255, 220, 150),
        'glow': (255, 180, 100),
        'elements': ['palace', 'scroll', 'lantern'],
        'mood': 'ancient',
    },
    '科幻': {
        'bg': [(5, 15, 35), (15, 40, 80), (30, 70, 130)],
        'accent': (100, 220, 255),
        'glow': (80, 180, 255),
        'elements': ['planet', 'rocket', 'nebula', 'circuit'],
        'mood': 'tech',
    },
    '游戏': {
        'bg': [(10, 30, 20), (25, 75, 50), (45, 130, 85)],
        'accent': (0, 255, 170),
        'glow': (100, 255, 200),
        'elements': ['pixel', 'controller', 'neon'],
        'mood': 'cyber',
    },
    '悬疑': {
        'bg': [(18, 15, 22), (45, 38, 55), (75, 65, 90)],
        'accent': (200, 180, 255),
        'glow': (160, 140, 220),
        'elements': ['eye', 'fog', 'moon', 'keyhole'],
        'mood': 'dark',
    },
    '武侠': {
        'bg': [(45, 28, 12), (105, 62, 28), (165, 95, 45)],
        'accent': (255, 215, 120),
        'glow': (255, 190, 80),
        'elements': ['sword', 'bamboo', 'ink'],
        'mood': 'classic',
    },
    '历史': {
        'bg': [(50, 35, 18), (115, 78, 38), (175, 118, 58)],
        'accent': (240, 210, 150),
        'glow': (220, 185, 120),
        'elements': ['seal', 'calligraphy', 'scroll'],
        'mood': 'classical',
    },
}

def lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

def draw_gradient(draw, w, h, colors):
    for y in range(h):
        t = y / h
        if len(colors) == 3 and t > 0.5:
            t2 = (t - 0.5) * 2
            c = lerp(colors[1], colors[2], t2)
        else:
            t2 = t * 2 if len(colors) == 3 else t
            c = lerp(colors[0], colors[1], min(t2, 1))
        draw.line([(0, y), (w, y)], fill=c)

def draw_stars(draw, w, h, color, count=60):
    for _ in range(count):
        x = random.randint(0, w)
        y = random.randint(0, int(h * 0.7))
        r = random.choice([1, 1, 1, 2, 2, 3])
        alpha = random.randint(80, 220)
        c = (*color[:3], alpha)
        if r <= 2:
            draw.point((x, y), fill=c)
        else:
            draw.ellipse([x-r, y-r, x+r, y+r], fill=c)

def draw_mountain(draw, w, h, base_color, peak_y):
    pts = [(0, h)]
    x = 0
    while x < w + 20:
        px = x + random.randint(30, 80)
        py = peak_y + random.randint(-40, 40)
        pts.append((px, py))
        x = px
    pts.append((w, h))
    if len(pts) >= 3:
        dark = tuple(max(0, c - 40) for c in base_color)
        draw.polygon(pts, fill=dark)

def draw_flame(draw, cx, cy, color, size=40):
    for i in range(8):
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(size * 0.3, size)
        fx = cx + math.cos(angle) * dist
        fy = cy - abs(math.sin(angle)) * dist * 1.5
        r = random.randint(4, 14)
        alpha = random.randint(100, 230)
        c = (*color[:3], alpha)
        draw.ellipse([fx-r, fy-r*1.6, fx+r, fy+r*0.7], fill=c)

def draw_dragon_silhouette(draw, w, h, color):
    body_pts = []
    sx, sy = w * 0.15, h * 0.55
    body_pts.append((sx, sy))
    for i in range(12):
        sx += random.randint(20, 45)
        sy += random.randint(-25, 20)
        body_pts.append((sx, min(sy, h * 0.85)))
    for i in range(len(body_pts) - 1):
        p1, p2 = body_pts[i], body_pts[i+1]
        width = 4 + int(6 * math.sin(i * 0.8))
        dark = tuple(max(0, c - 30) for c in color)
        draw.line([p1, p2], fill=dark, width=width)
    hx, hy = body_pts[-1]
    head_r = 16
    draw.ellipse([hx-head_r, hy-head_r, hx+head_r, hy+head_r], fill=color)

def draw_circle_glow(draw, cx, cy, radius, color, layers=5):
    for i in range(layers, 0, -1):
        r = radius * i / layers
        alpha = int(40 * (layers - i + 1) / layers)
        c = (*color[:3], alpha)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=c)

def draw_ink_wash(draw, w, h, color):
    for _ in range(15):
        x = random.randint(0, w)
        y = random.randint(int(h * 0.2), int(h * 0.8))
        rx = random.randint(30, 120)
        ry = random.randint(40, 180)
        alpha = random.randint(15, 45)
        c = (*color[:3], alpha)
        draw.ellipse([x-rx, y-ry, x+rx, y+ry], fill=c)

def draw_nebula_clouds(draw, w, h, colors):
    for _ in range(20):
        x = random.randint(-50, w + 50)
        y = random.randint(-30, int(h * 0.6))
        rx = random.randint(40, 150)
        ry = random.randint(25, 80)
        c = random.choice(colors)
        alpha = random.randint(10, 35)
        col = (*c[:3], alpha)
        draw.ellipse([x-rx, y-ry, x+rx, y+ry], fill=col)

def draw_circuit_lines(draw, w, h, color):
    for _ in range(12):
        x1 = random.randint(0, w)
        y1 = random.randint(0, h)
        direction = random.choice(['h', 'v'])
        if direction == 'h':
            x2 = x1 + random.randint(30, 120)
            y2 = y1
        else:
            x2 = x1
            y2 = y1 + random.randint(30, 100)
        alpha = random.randint(30, 80)
        c = (*color[:3], alpha)
        draw.line([(x1,y1),(x2,y2)], fill=c, width=1)
        draw.ellipse([x2-3, y2-3, x2+3, y2+3], fill=c)

def draw_bamboo_stalk(draw, bx, h, color):
    seg_h = random.randint(25, 40)
    y = h
    while y > h * 0.15:
        sw = random.randint(2, 4)
        ny = y - seg_h
        dark = tuple(max(0, c - 20) for c in color)
        draw.line([(bx, y), (bx, max(ny, h*0.1))], fill=dark, width=sw)
        if y < h * 0.9:
            lw = random.randint(8, 16)
            lh = random.randint(3, 5)
            draw.line([(bx-lw, y-seg_h*0.3), (bx+lw, y-seg_h*0.3)], fill=color, width=lh)
        y = ny
        seg_h = random.randint(20, 38)

def draw_sword(draw, x, y, color, scale=1):
    blade_len = int(130 * scale)
    handle_len = int(25 * scale)
    guard_w = int(22 * scale)
    dark = tuple(max(0, c - 25) for c in color)
    light = tuple(min(255, c + 60) for c in color)
    draw.polygon([
        (x, y), (x + 4*scale, y - blade_len),
        (x - 4*scale, y - blade_len)
    ], fill=light)
    draw.rectangle([x - guard_w//2, y, x + guard_w//2, y + int(6*scale)], fill=dark)
    draw.rectangle([x - 3*scale, y + int(6*scale), x + 3*scale, y + handle_len + int(6*scale)], fill=dark)
    draw.ellipse([x - 5*scale, y + handle_len + int(4*scale), x + 5*scale, y + handle_len + int(14*scale)], fill=color)

def draw_planet_ring(draw, cx, cy, r, color, tilt=0.3):
    dark = tuple(max(0, c - 40) for c in color)
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=dark)
    ring_outer = r * 1.8
    ring_inner = r * 1.4
    ring_h = int(ring_outer * tilt)
    draw.arc([cx-ring_outer, cy-ring_h, cx+ring_outer, cy+ring_h], 0, 360, fill=color, width=3)

def draw_text_card(draw, w, h, title, author, category, theme):
    card_y = int(h * 0.58)
    card_h = int(h * 0.36)
    pad = 18
    
    bg_dark = tuple(max(0, int(c * 0.15)) for c in theme['bg'][0])
    overlay = (*bg_dark, 180)
    draw.rectangle([pad, card_y, w - pad, card_y + card_h], fill=overlay)
    
    border = (*theme['accent'], 100)
    draw.rectangle([pad, card_y, w - pad, card_y + card_h], outline=border, width=1)
    
    title_font = try_font(32, bold=True)
    author_font = try_font(17)
    cat_font = try_font(13)
    
    lines = []
    current = ''
    for ch in title:
        test = current + ch
        bbox = title_font.getbbox(test)
        if bbox[2] - bbox[0] <= w - 56:
            current = test
        else:
            if current: lines.append(current)
            current = ch
    if current: lines.append(current)
    
    ty = card_y + 22
    for line in lines:
        bbox = title_font.getbbox(line)
        tw = bbox[2] - bbox[0]
        draw.text(((w - tw) // 2, ty), line, fill=(255, 248, 235, 255), font=title_font)
        ty += 42
    
    sep_y = ty + 6
    draw.line([(45, sep_y), (w - 45, sep_y)], fill=(*theme['accent'], 160), width=1)
    
    abbox = author_font.getbbox(author)
    aw = abbox[2] - abbox[0]
    draw.text(((w - aw) // 2, sep_y + 12), author, fill=(210, 200, 185, 220), font=author_font)
    
    cat_text = f'「{category}」'
    cbbox = cat_font.getbbox(cat_text)
    cw = cbbox[2] - cbbox[0]
    draw.text(((w - cw) // 2, card_y + card_h - 32), cat_text, fill=(*theme['accent'], 180), font=cat_font)

def generate_cover(novel):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    
    theme = THEMES.get(novel.category, THEMES['玄幻'])
    
    draw_gradient(draw, W, H, theme['bg'])
    
    mood = theme['mood']
    elem = theme['elements']
    glow_c = theme['glow']
    accent = theme['accent']
    
    if mood in ('mystical', 'tech'):
        draw_stars(draw, W, H, accent, count=70 if mood == 'mystical' else 40)
    
    if mood == 'mystical':
        draw_circle_glow(draw, W * 0.7, H * 0.25, 80, glow_c, layers=6)
        if 'mountain' in elem or random.random() > 0.4:
            draw_mountain(draw, W, H, theme['bg'][1], H * 0.55)
            draw_mountain(draw, W, H, theme['bg'][0], H * 0.62)
        if 'flame' in elem or random.random() > 0.5:
            draw_flame(draw, W * 0.25, H * 0.48, (255, 150, 50), 50)
            draw_flame(draw, W * 0.3, H * 0.45, (255, 200, 80), 35)
        if 'dragon' in elem or random.random() > 0.6:
            draw_dragon_silhouette(draw, W, H, glow_c)
    
    elif mood == 'modern':
        for i in range(5):
            y = int(H * 0.3) + i * 35
            alpha = 30 + i * 15
            draw.line([(30, y), (W - 30, y)], fill=(*glow_c[:3], alpha), width=1)
        draw_circle_glow(draw, W * 0.5, H * 0.35, 60, glow_c, layers=4)
    
    elif mood == 'ancient':
        draw_ink_wash(draw, W, H, glow_c)
        draw_circle_glow(draw, W * 0.6, H * 0.3, 50, accent, layers=4)
        if 'lantern' in elem:
            for lx in [W * 0.2, W * 0.8]:
                ly = H * 0.35 + random.randint(-20, 20)
                draw.ellipse([lx-10, ly-14, lx+10, ly+14], fill=(*accent, 150))
                draw.line([(lx, ly+14), (lx, ly+35)], fill=(*accent, 100), width=2)
    
    elif mood == 'tech':
        draw_nebula_clouds(draw, W, H, [glow_c, accent, (100, 150, 255)])
        draw_circuit_lines(draw, W, H, glow_c)
        if 'planet' in elem:
            draw_planet_ring(draw, int(W * 0.65), int(H * 0.35), 35, glow_c)
        draw_circle_glow(draw, W * 0.3, H * 0.4, 45, accent, layers=5)
    
    elif mood == 'cyber':
        for i in range(8):
            y = int(H * 0.15) + i * 30
            c = glow_c if i % 2 == 0 else accent
            alpha = 25 + (i % 3) * 20
            draw.line([(0, y), (W, y)], fill=(*c[:3], alpha), width=1)
        draw_circle_glow(draw, W * 0.5, H * 0.38, 55, glow_c, layers=5)
    
    elif mood == 'dark':
        draw_ink_wash(draw, W, H, glow_c)
        mx, my = W * 0.5, H * 0.38
        draw.ellipse([mx-30, my-30, mx+30, my+30], fill=(*glow_c[:3], 40))
        draw.ellipse([mx-15, my-15, mx+15, my+15], fill=(*accent[:3], 80))
    
    elif mood == 'classic':
        draw_ink_wash(draw, W, H, glow_c)
        if 'bamboo' in elem:
            draw_bamboo_stalk(draw, W * 0.12, H, glow_c)
            draw_bamboo_stalk(draw, W * 0.05, H, (glow_c[0]//2, glow_c[1]//2, glow_c[2]//2))
        if 'sword' in elem or random.random() > 0.4:
            draw_sword(draw, int(W * 0.68), int(H * 0.55), accent, 1.0)
        draw_circle_glow(draw, W * 0.5, H * 0.3, 40, glow_c, layers=4)
    
    elif mood == 'classical':
        draw_ink_wash(draw, W, H, glow_c)
        draw_circle_glow(draw, W * 0.5, H * 0.32, 50, accent, layers=5)
        for i in range(3):
            sx = W * (0.25 + i * 0.25)
            sy = H * 0.45 + random.randint(-15, 15)
            draw.ellipse([sx-4, sy-4, sx+4, sy+4], fill=(*accent, 120))
    
    draw_text_card(draw, W, H, novel.title, novel.author, novel.category, theme)
    
    rgb = Image.new('RGB', img.size, (255, 255, 255))
    rgb.paste(img, mask=img.split()[-1])
    return rgb

updated = 0
for novel in Novel.objects.all().order_by('id'):
    random.seed(novel.id * 42 + hash(novel.title))
    img = generate_cover(novel)
    
    fname = f'cover_{novel.id:02d}.jpg'
    fpath = os.path.join(COVER_DIR, fname)
    img.save(fpath, 'JPEG', quality=93)
    
    novel.cover = f'/media/covers/{fname}'
    novel.save(update_fields=['cover'])
    updated += 1
    print(f'  OK [{novel.id}] {novel.title} ({novel.category})')

print(f'\nDone! {updated}/{Novel.objects.count()} artistic covers generated.')
