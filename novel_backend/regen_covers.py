import os, sys, django, requests, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')
django.setup()

from novels.models import Novel
from urllib.parse import quote

API = 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image'
SIZE = 'portrait_4_3'
COVER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'covers')

PROMPTS = {
    '斗破苍穹': 'A Chinese fantasy book cover, young warrior surrounded by purple flames, phoenix flying behind, dramatic cinematic lighting, dark background with gold accents, professional book cover design',
    '完美世界': 'A Chinese xianxia novel cover, lone cultivator standing on mountain cliff looking at starry sky, ancient deer in clouds, epic atmosphere, dark mystical background, gold border frame',
    '庆余年': 'Historical Chinese novel cover, elegant scholar in white robe holding folding fan, ancient palace in snow, ink wash painting style, refined elegant design, dark red tones',
    '凡人修仙传': 'Xianxia cultivation novel cover, daoist cultivator riding flying sword above sea of clouds, distant mountain palace, ethereal misty green-blue tones, traditional chinese art style',
    '全职高手': 'Esports gaming novel cover, professional gamer silhouette with glowing keyboard, neon blue RGB lighting, modern digital art style, dark tech background',
    '赘婿': 'Chinese historical romance cover, clever merchant in song dynasty robes, jiangnan water town with lanterns, classical chinese painting, warm golden tones',
    '大主宰': 'Epic fantasy battle cover, young warrior summoning golden thunder bird, glowing runes and energy effects, dramatic action pose, fiery orange-red palette',
    '雪中悍刀行': 'Wuxia novel cover, swordsman in white robe walking through heavy snow, ornate saber drawn, bamboo forest, ink wash minimalist style, cold blue-white tones',
    '择天记': 'Mystical cultivation cover, young taoist under starry constellation sky, ancient temple silhouette, glowing star patterns, deep purple cosmic background',
    '仙逆': 'Dark xianxia cover, stoic cultivator in black robe inside ancient tomb, eerie green glow, floating runes, mysterious ominous atmosphere, dark tones',
    '一念永恒': 'Light cultivation novel cover, taoist meditating under blooming peach tree, white crane flying, soft pastel pink-white tones, peaceful immortal art',
    '星辰变': 'Cosmic cultivation cover, cultivator absorbing star energy, dragon coiling around him, brilliant nebula galaxy background, deep space blue-purple palette',
    '盘龙': 'Western fantasy magic cover, powerful mage casting elemental spell, fire ice lightning swirling, dragon roaring, dramatic magical explosion of colors',
    '飞刀之后': 'Classic wuxia cover, black robed figure throwing knife under full moon, falling cherry blossoms, cinematic action scene, moonlit silver-dark palette',
    '我欲封天': 'Epic xianxia cover, cultivator on mountain peak, purple lightning storm sealing the sky, dramatic god-like pose, electric purple-dark tones',
    '永夜君王': 'Dark fantasy cover, king on throne under endless starry night, glowing crown, royal darkness, deep midnight blue with silver starlight',
    '校花的贴身高手': 'Urban romance comedy cover, confident young man silhouette in modern city campus, warm daylight, clean modern design style',
    '神墓': 'Ancient tomb mystery cover, warrior emerging from divine tomb, glowing weapons floating, mystical fog, golden-brown ancient artifact tones',
    '遮天': 'Epic cultivation cover, heroic figure before giant bronze cauldron, primordial star sea sky, monumental scale, bronze-gold-cosmic blue palette',
    '盗墓笔记': 'Adventure thriller cover, explorer with torch inside ancient tomb, stone coffins and artifacts, mysterious greenish glow, suspenseful dark tones',
    '鬼吹灯': 'Tomb raiding adventure cover, raider with compass in dark corridor, ancient murals on walls, traps and mysteries, eerie orange torchlight',
    '武动乾坤': 'Martial arts cultivation cover, young warrior gathering cosmic qi energy between hands, stone arena, explosive golden energy aura',
    '元尊': 'Source power cultivation cover, hero with black dragon spirit behind, glowing source patterns, dramatic contrast of light and shadow, gold-black palette',
    '剑来': 'Literary wuxia cover, young swordsman walking through rainy ancient town, stone bridge and lanterns, melancholic ink painting style, gray-green tones',
    '流浪地球': 'Sci-fi epic cover, Earth with massive thrusters, frozen wasteland landscape, dying sun in background, cinematic blue-white sci-fi palette',
    '三体': 'Hard sci-fi cover, three suns in alien sky, mysterious civilization, dark space with red suns, minimalist futuristic design',
}

DEFAULT = 'epic chinese fantasy novel book cover, dramatic lighting, professional design, dark rich colors'

os.makedirs(COVER_DIR, exist_ok=True)
session = requests.Session()
updated = 0

for n in Novel.objects.all().order_by('id'):
    prompt = PROMPTS.get(n.title, DEFAULT)
    url = f'{API}?prompt={quote(prompt)}&image_size={SIZE}'
    
    fname = f'cover_{n.id:02d}.jpg'
    fpath = os.path.join(COVER_DIR, fname)
    
    try:
        resp = session.get(url, timeout=30)
        if resp.status_code == 200:
            content_type = resp.headers.get('Content-Type', '')
            if 'image' in content_type or len(resp.content) > 5000:
                with open(fpath, 'wb') as f:
                    f.write(resp.content)
                n.cover = f'/media/covers/{fname}'
                n.save(update_fields=['cover'])
                updated += 1
                size_kb = len(resp.content) // 1024
                print(f'  OK [{n.id}] {n.title} -> {fname} ({size_kb}KB)')
            else:
                print(f'  SKIP [{n.id}] {n.title} -> not image ({len(resp.content)}B)')
        else:
            print(f'  ERR [{n.id}] {n.title} -> HTTP {resp.status_code}')
    except Exception as e:
        print(f'  FAIL [{n.id}] {n.title} -> {e}')
    
    time.sleep(0.5)

print(f'\nDone! {updated}/{Novel.objects.count()} covers regenerated.')
