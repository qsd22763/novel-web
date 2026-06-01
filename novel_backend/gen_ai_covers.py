import os, sys, django, requests, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')
django.setup()

from novels.models import Novel
from urllib.parse import quote

API = 'https://image.pollinations.ai/prompt/'
W, H = 400, 560
COVER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'covers')

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

PROMPTS = {
    '斗破苍穹': 'Chinese fantasy xianxia novel book cover art, a handsome young warrior in black martial arts robe surrounded by swirling purple flames and fire, ancient chinese phoenix with golden wings flying behind him, dramatic cinematic lighting, dark mystical purple background with floating particles, professional digital illustration, ultra detailed, 8k quality, epic composition',
    '完美世界': 'Chinese cultivation novel cover art, a lone young cultivator in white robes standing on edge of a majestic mountain cliff looking up at vast starry sky, a mysterious glowing deer among ethereal clouds, oriental fantasy epic scene, atmospheric mist and light beams, deep blue and silver color palette, cinematic digital painting, highly detailed',
    '遮天': 'Xianxia novel cover art, a heroic cultivator in ancient armor standing defiantly before a gigantic bronze cauldron with dragon carvings, primordial star sea filling the sky with multiple suns, monumental immortal chinese fantasy scene, bronze gold and cosmic blue tones, epic scale composition, professional fantasy illustration',
    '凡人修仙传': 'Cultivation novel cover art, a daoist cultivator in elegant green robe riding a glowing flying sword above a vast sea of clouds at sunset, distant mountain palace floating among misty peaks, ethereal oriental fantasy scene, teal green and gold tones, cinematic god rays, professional digital art',
    '庆余年': 'Historical chinese romance novel cover art, an elegant young scholar in flowing white hanfu holding a folding fan with confident smile, grand ancient chinese palace architecture with gentle snow falling, ink wash painting style mixed with realistic details, refined elegant mood, warm red and gold color scheme',
    '赘婿': 'Chinese historical comedy novel cover art, a clever young merchant in song dynasty hanfu holding folding fan, picturesque jianghu water town with painted boats and red lanterns on river, classical chinese painting aesthetic, warm golden sunset tones, charming atmosphere, detailed traditional art',
    '吞噬星空': 'Sci-fi cultivation novel cover art, a futuristic warrior in sleek powered armor absorbing cosmic energy from a swirling black hole, stars galaxies and nebulae surrounding him, brilliant space opera scene, deep space blue purple and gold energy effects, epic sci-fi digital art, cinematic lighting',
    '全职高手': 'Esports gaming novel cover art, a professional gamer silhouette wearing headphones sitting before a glowing RGB mechanical keyboard with hands on keys, neon blue cyberpunk gaming arena background with audience silhouettes, dramatic blue lighting, modern game poster design, tech aesthetic',
    '诡秘之主': 'Mystery supernatural novel cover art, a mysterious gentleman in victorian steampunk attire holding an ornate pocket watch with golden gears floating around, gothic clock tower and foggy london street background, supernatural mystery atmosphere, sepia bronze and mysterious green tones, gothic fantasy art',
    '大道朝天': 'Philosophical cultivation novel cover art, an ascetic taoist immortal in white robes standing on a cloud path leading to heavenly gates in clouds, ethereal divine light shining down, mountain peaks below, philosophical serene mood, white gold and celestial blue tones, transcendent art style',
    '雪中悍刀行': 'Wuxia novel cover art, a white robed young swordsman walking through heavy snowfall holding an ornate golden saber, bamboo forest shrouded in thick mist, wuxia ink wash minimalist style combined with realism, cold blue white color palette, melancholic heroic atmosphere, chinese brush art',
    '择天记': 'Mystical cultivation novel cover art, a young taoist boy meditating under a vast starry sky with glowing constellation patterns forming a zodiac circle, ancient temple silhouette in distance, deep purple cosmic blue gradient background, mystical oriental fantasy atmosphere, magical stars',
    '将夜': 'Wuxia literary novel cover art, a young scholar with a sword hidden inside a book box walking through snow-covered imperial capital city, warm orange lanterns illuminating cold streets at dusk, wuxia literary fusion style, cold blue and warm orange contrast, poetic atmosphere',
    '牧神记': 'Fantasy novel cover art, a young man with glowing divine eyes seeing through layers of reality, multiple transparent worlds overlapping with gods and demons visible in each layer, mystical multi-layered translucent colors, surreal fantasy composition, vibrant magical artwork',
    '全球高武': 'Urban martial arts action novel cover art, a modern martial artist in sportswear performing an impossible high kick with visible energy shockwave effect, modern city skyline with skyscrapers in background, dynamic action pose, urban martial arts theme, blue and gold energy effects',
    '元尊': 'Cultivation novel cover art, a young heroic figure with a majestic black dragon spirit coiling protectively behind him, glowing source power patterns and runes floating in air, dramatic contrast of light and shadow, gold black and dragon green palette, powerful epic fantasy illustration',
    '武动乾坤': 'Martial arts novel cover art, a young warrior gathering swirling cosmic qi energy between both hands in an ancient stone arena, explosive golden energy aura emanating outward, epic chinese fantasy martial arts scene, gold energy and dark stone palette, dynamic action composition',
    '大主宰': 'Epic fantasy battle novel cover art, a young warrior in battle stance summoning a giant golden thunder roc bird with lightning bolts, ancient chinese fantasy battle scene with energy effects, fiery orange gold palette, epic dramatic action pose, explosive composition',
    '仙逆': 'Dark xianxia novel cover art, a stoic young cultivator in dark robes standing inside an ancient stone tomb chamber, eerie green magical glow and floating ancient runes around him, dark mysterious xianxia atmosphere, deep green and black tones, ominous fantasy art',
    '求魔': 'Tragic dark fantasy novel cover art, a tragic cultivation protagonist standing torn between two worlds one of light one of darkness, dual-toned half bright golden half dark shadow composition, emotional dark fantasy theme, torn fate visual metaphor, dramatic contrast',
    '我欲封天': 'Epic xianxia novel cover art, a young cultivator sitting cross-legged on mountain peak with massive purple lightning storm sealing the entire sky above, epic god-like meditation pose, electric purple storm and dark tones, overwhelming power visual, cinematic fantasy',
    '一念永恒': 'Light cultivation novel cover art, a young taoist in pure white robes meditating peacefully under a blooming pink peach tree with petals falling, a graceful white crane flying overhead, soft immortal chinese fantasy art, pastel pink white dreamy peaceful tones',
    '星辰变': 'Cosmic cultivation novel cover art, a young cultivator absorbing brilliant star energy from cosmos, an ancient cosmic dragon coiling protectively around his body, brilliant colorful nebula galaxy background, deep space blue purple and gold, epic space fantasy art',
    '盘龙': 'Western fantasy magic novel cover art, a powerful western mage casting spectacular elemental magic spell with fire ice and lightning all swirling together, an ancient roaring dragon behind him, western fantasy vibrant multicolor energy explosion, magical masterpiece',
    '剑来': 'Literary wuxia novel cover art, a young swordsman in simple green robes walking through rainy ancient town with stone bridge, warm lantern glow illuminating the melancholic scene, literary wuxia ink painting style, gray green rainy tones, poetic atmosphere',
    '万古最强宗': 'Epic sect novel cover art, a vast majestic mountain sect gate with floating palaces and disciples in robes amidst immortal mist clouds, grand monumental scale, epic xianxia book cover, golden immortal and mist palette, awe-inspiring composition',
    '流浪地球': 'Hard sci-fi movie-style cover art, planet Earth with massive planetary thrusters attached to surface propelling it, frozen ice wasteland landscape, dying red sun in distant sky, cinematic science fiction movie poster style, blue white cold sci-fi palette, epic scale',
    '三体': 'Hard science fiction cover art, three alien suns burning in a strange sky over mysterious civilization ruins, dark void of space, minimalist futuristic design, ominous red and dark blue color scheme, hard sci-fi intellectual atmosphere, clean geometric composition',
}

DEFAULT = 'beautiful chinese fantasy novel book cover art, dramatic cinematic lighting, professional digital illustration, rich detailed artwork, epic composition'

session = requests.Session()
session.headers.update(HEADERS)
os.makedirs(COVER_DIR, exist_ok=True)

updated = 0
for novel in Novel.objects.all().order_by('id'):
    prompt = PROMPTS.get(novel.title, DEFAULT)
    seed = (novel.id * 137 + hash(novel.title) % 10000) % (2**32)
    url = f'{API}{quote(prompt)}?width={W}&height={H}&nologo=true&seed={seed}'
    
    fname = f'cover_{novel.id:02d}.jpg'
    fpath = os.path.join(COVER_DIR, fname)
    
    for attempt in range(3):
        try:
            resp = session.get(url, timeout=90)
            if resp.status_code == 200:
                ct = resp.headers.get('Content-Type', '')
                if 'image' in ct and len(resp.content) > 20000:
                    with open(fpath, 'wb') as f:
                        f.write(resp.content)
                    novel.cover = f'/media/covers/{fname}'
                    novel.save(update_fields=['cover'])
                    updated += 1
                    size_kb = len(resp.content) // 1024
                    print(f'  OK [{novel.id:02d}] {novel.title} -> {fname} ({size_kb}KB)')
                    break
                else:
                    print(f'  RETRY [{novel.id:02d}] {novel.title} -> small ({len(resp.content)}B)')
            else:
                print(f'  ERR [{novel.id:02d}] {novel.title} -> HTTP {resp.status_code}')
        except Exception as e:
            print(f'  FAIL [{novel.id:02d}] {novel.title} -> {e} (attempt {attempt+1})')
        time.sleep(3)
    else:
        print(f'  SKIP [{novel.id:02d}] {novel.title}')
    
    time.sleep(1.5)

print(f'\nDone! {updated}/{Novel.objects.count()} AI covers generated.')
