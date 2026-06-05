import os, sys, django, requests, time, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')
django.setup()

from novels.models import Novel
from urllib.parse import quote

API = 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image'
SIZE = 'portrait_4_3'
COVER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'covers')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'Referer': 'http://localhost:5173/',
}

PROMPTS = {
    '斗破苍穹': 'A young warrior in black martial arts robe surrounded by swirling purple flames, ancient chinese phoenix flying behind, dramatic fantasy book cover art, cinematic lighting, dark purple and gold color scheme, ultra detailed digital painting',
    '完美世界': 'A lone young cultivator in white robes standing on a mountain cliff edge, looking up at vast starry sky with a mystical deer among clouds, oriental fantasy epic scene, atmospheric mist, deep blue and silver tones, cinematic composition',
    '庆余年': 'An elegant young scholar in flowing white hanfu holding a folding fan, grand ancient chinese palace with snow falling gently, ink wash painting style book cover, refined elegant mood, warm red and gold palette',
    '凡人修仙传': 'A daoist cultivator in green robes riding a glowing flying sword above a vast sea of clouds, distant mountain palace floating in mist, ethereal oriental fantasy scene, teal-green and gold tones, cinematic light rays',
    '全职高手': 'A professional esports gamer silhouette wearing headphones sitting before a glowing RGB mechanical keyboard, neon blue cyberpunk gaming arena background, dramatic blue lighting, modern game cover art style, tech aesthetic',
    '赘婿': 'A clever young merchant in song dynasty hanfu holding a folding fan with a confident smile, jiangnan water town with painted boats and red lanterns, classical chinese painting style, warm golden sunset tones',
    '大主宰': 'A young warrior in battle stance summoning a giant golden thunder roc bird, lightning and energy swirling around, ancient chinese fantasy battle scene, fiery orange-gold palette, epic dramatic composition',
    '雪中悍刀行': 'A white-robed young swordsman walking through heavy snowfall holding an ornate golden saber, bamboo forest shrouded in mist, wuxia ink painting minimalist style, cold blue-white color palette',
    '择天记': 'A young taoist boy meditating under a vast starry sky with glowing constellation patterns, ancient temple silhouette in distance, mystical oriental fantasy atmosphere, deep purple-cosmic blue gradient',
    '仙逆': 'A stoic young cultivator in dark robes standing inside an ancient stone tomb, eerie green magical glow and floating runes around him, dark xianxia mysterious atmosphere, deep green-black tones',
    '一念永恒': 'A young taoist in pure white robes meditating peacefully under a blooming pink peach tree, a white crane flying overhead, soft immortal chinese fantasy art, pastel pink-white dreamy tones',
    '星辰变': 'A young cultivator absorbing brilliant star energy from cosmos, an ancient cosmic dragon coiling protectively around him, brilliant nebula galaxy background, deep space blue-purple-epic fantasy cover',
    '盘龙': 'A powerful western mage casting spectacular elemental magic spell, fire ice and lightning swirling together, an ancient dragon roaring behind him, western fantasy book cover, vibrant multicolor energy',
    '飞刀之后': 'A mysterious black-robed figure throwing a gleaming flying knife under bright full moonlight, falling cherry blossom petals everywhere, classic wuxia poster cinematic scene, moonlit silver-dark palette',
    '我欲封天': 'A young cultivator sitting cross-legged on a mountain peak, massive purple lightning storm sealing the entire sky above, epic god-like xianxia pose, electric purple-storm-dark tones',
    '永夜君王': 'A dark imposing king sitting on an ornate throne under endless star-filled night sky, wearing a glowing crown, royal darkness fantasy book cover, midnight blue-silver starlight palette',
    '校花的贴身高手': 'A confident stylish young man in black suit standing in a modern university campus courtyard, urban chinese romance novel cover, warm daylight clean modern design',
    '神墓': 'An ancient warrior emerging from a divine tomb with glowing weapons and runes floating around, mystical fog and golden light beams, epic chinese fantasy cover, bronze-gold-mysterious tones',
    '遮天': 'A heroic cultivator standing defiantly before a gigantic ancient bronze cauldron, primordial star sea filling the sky, monumental immortal chinese fantasy art, bronze-gold-cosmic blue palette',
    '盗墓笔记': 'A young explorer holding a torch inside a dark ancient ming dynasty tomb chamber, glowing artifacts and stone coffins visible, mysterious adventure thriller cover, greenish torchlight-dark tones',
    '鬼吹灯': 'A tomb raider holding compass and oil lamp in a dark stone corridor, ancient murals on walls and hidden traps, mystery thriller book cover, warm orange torchlight-shadowy tones',
    '武动乾坤': 'A young warrior gathering swirling cosmic qi energy between both hands in an ancient stone arena, explosive golden energy aura, epic chinese fantasy martial arts cover, gold-energy-dark palette',
    '元尊': 'A young heroic figure with a majestic black dragon spirit coiling behind him, glowing source power patterns in air, dramatic contrast of light and shadow, gold-black-dragon palette',
    '剑来': 'A young swordsman in simple green robes walking through a rainy ancient town with stone bridge, warm lantern glow illuminating the melancholic scene, literary wuxia ink painting style, gray-green-rainy tones',
    '万古最强宗': 'A vast mountain sect gate with floating palaces and disciples in robes amidst immortal mist clouds, grand scale epic xianxia book cover, golden-immortal-mist palette',
    '流浪地球': 'Sci-fi epic scene of planet Earth with massive planetary thrusters attached to surface, frozen wasteland landscape, dying red sun in distant sky, cinematic blue-white sci-fi movie poster style',
    '三体': 'Hard science fiction scene showing three suns in alien sky over a mysterious civilization ruin, dark space with three red suns, minimalist futuristic design, ominous red-dark-blue palette',
    '吞噬星空': 'A futuristic sci-fi warrior in powered armor absorbing cosmic energy from a black hole, stars and galaxies swirling around, epic space opera cover, deep space blue-purple-gold energy',
    '诡秘之主': 'A mysterious gentleman in victorian steampunk attire holding a pocket watch with gears floating around, gothic clock tower and foggy london street, mysterious supernatural atmosphere, sepia-bronze-mysterious',
    '大道朝天': 'An ascetic taoist immortal standing on a cloud path leading to heavenly gates, ethereal light and mountain peaks, philosophical cultivation art, white-gold-celestial tones',
    '将夜': 'A young scholar with a sword hidden in a book box walking through snow-covered imperial capital, lantern-lit streets at dusk, wuxia-literary fusion style, cold blue-warm orange contrast',
    '牧神记': 'A young man with divine eyes seeing through reality layers, multiple transparent worlds overlapping, gods and demons in background, mystical fantasy cover, multi-layered translucent colors',
    '全球高武': 'A modern martial artist in sportswear performing an impossible high kick with energy shockwave, city skyline in background, urban martial arts action cover, dynamic blue-gold energy',
    '求魔': 'A tragic cultivation protagonist standing between two worlds - one of light one of darkness, torn fate theme, dual-toned half-light-half-dark composition, emotional dark fantasy cover',
}

DEFAULT = 'epic chinese fantasy novel book cover, dramatic cinematic lighting, professional illustration, rich detailed artwork'

session = requests.Session()
session.headers.update(HEADERS)
os.makedirs(COVER_DIR, exist_ok=True)

updated = 0
for novel in Novel.objects.all().order_by('id'):
    prompt = PROMPTS.get(novel.title, DEFAULT)
    url = f'{API}?prompt={quote(prompt)}&image_size={SIZE}'
    
    fname = f'cover_{novel.id:02d}.jpg'
    fpath = os.path.join(COVER_DIR, fname)
    
    for attempt in range(3):
        try:
            resp = session.get(url, timeout=60)
            if resp.status_code == 200:
                ct = resp.headers.get('Content-Type', '')
                if 'image' in ct and len(resp.content) > 10000:
                    with open(fpath, 'wb') as f:
                        f.write(resp.content)
                    novel.cover = f'/media/covers/{fname}'
                    novel.save(update_fields=['cover'])
                    updated += 1
                    size_kb = len(resp.content) // 1024
                    print(f'  OK [{novel.id}] {novel.title} -> {fname} ({size_kb}KB)')
                    break
                else:
                    print(f'  RETRY [{novel.id}] {novel.title} -> not image ({len(resp.content)}B, {ct})')
            else:
                print(f'  ERR [{novel.id}] {novel.title} -> HTTP {resp.status_code}')
        except Exception as e:
            print(f'  FAIL [{novel.id}] {novel.title} -> {e} (attempt {attempt+1})')
        time.sleep(2)
    else:
        print(f'  SKIP [{novel.id}] {novel.title} -> all attempts failed')
    
    time.sleep(1)

print(f'\nDone! {updated}/{Novel.objects.count()} covers regenerated.')
