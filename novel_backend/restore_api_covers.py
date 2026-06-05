import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')
django.setup()

from novels.models import Novel
from urllib.parse import quote

API = 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image'
SIZE = 'portrait_4_3'

PROMPTS = {
    '斗破苍穹': 'A young warrior in black martial arts robe surrounded by swirling purple flames, ancient chinese phoenix flying behind, dramatic fantasy book cover art, cinematic lighting, ultra detailed digital painting',
    '完美世界': 'A lone young cultivator in white robes standing on mountain cliff looking up at vast starry sky with mystical deer among clouds, oriental fantasy epic scene, atmospheric mist, cinematic',
    '庆余年': 'An elegant young scholar in flowing white hanfu holding folding fan, grand ancient chinese palace with snow falling, ink wash painting style book cover, refined elegant mood',
    '凡人修仙传': 'A daoist cultivator in green robes riding glowing flying sword above sea of clouds, distant mountain palace floating in mist, ethereal oriental fantasy scene, cinematic light rays',
    '全职高手': 'A professional esports gamer silhouette wearing headphones before glowing RGB keyboard, neon blue cyberpunk gaming arena, dramatic blue lighting, modern game cover art',
    '赘婿': 'A clever young merchant in song dynasty hanfu holding folding fan confidently, jiangnan water town with painted boats and red lanterns, classical chinese painting style',
    '大主宰': 'A young warrior summoning giant golden thunder roc bird with lightning energy swirling, ancient chinese fantasy battle scene, fiery orange-gold epic composition',
    '雪中悍刀行': 'A white-robed young swordsman walking through heavy snow holding ornate golden saber, bamboo forest in mist, wuxia ink painting minimalist style',
    '择天记': 'A young taoist boy under starry constellation sky with ancient temple silhouette, glowing star patterns, mystical oriental fantasy atmosphere',
    '仙逆': 'A stoic young cultivator in dark robes inside ancient stone tomb, eerie green magical glow and floating runes, dark xianxia mysterious atmosphere',
    '一念永恒': 'A young taoist in pure white robes meditating under blooming pink peach tree, white crane flying, soft immortal chinese fantasy art, dreamy pastel tones',
    '星辰变': 'A young cultivator absorbing brilliant star energy from cosmos, ancient cosmic dragon coiling around him, brilliant nebula galaxy background, epic space fantasy',
    '盘龙': 'A powerful western mage casting spectacular elemental magic spell, fire ice lightning swirling, ancient dragon roaring behind, western fantasy vibrant multicolor',
    '飞刀之后': 'A mysterious black-robed figure throwing gleaming flying knife under bright full moonlight, falling cherry blossom petals, classic wuxia cinematic poster',
    '我欲封天': 'A young cultivator on mountain peak with massive purple lightning storm sealing sky above, epic god-like xianxia pose, electric purple-storm-dark tones',
    '永夜君王': 'A dark imposing king on throne under endless star-filled night sky wearing glowing crown, royal darkness fantasy, midnight blue-silver starlight',
    '校花的贴身高手': 'A confident stylish young man in black suit in modern university campus courtyard, urban chinese romance novel cover, warm daylight modern design',
    '神墓': 'An ancient warrior emerging from divine tomb with glowing weapons and runes floating, mystical fog golden light beams, epic chinese fantasy bronze-gold-mysterious',
    '遮天': 'A heroic cultivator standing before gigantic ancient bronze cauldron, primordial star sea filling sky, monumental immortal chinese fantasy bronze-cosmic-blue',
    '盗墓笔记': 'A young explorer holding torch inside dark ancient ming dynasty tomb chamber, glowing artifacts stone coffins, mysterious adventure thriller greenish torchlight',
    '鬼吹灯': 'A tomb raider holding compass and oil lamp in dark stone corridor, ancient murals hidden traps, mystery thriller warm orange torchlight-shadowy',
    '武动乾坤': 'A young warrior gathering swirling cosmic qi energy between hands in ancient stone arena, explosive golden energy aura, epic martial arts gold-energy-dark',
    '元尊': 'A young heroic figure with majestic black dragon spirit coiling behind, glowing source power patterns, dramatic light-shadow contrast gold-black-dragon',
    '剑来': 'A young swordsman in simple green robes walking through rainy ancient town with stone bridge, warm lantern glow melancholic literary wuxia ink gray-green-rainy',
    '万古最强宗': 'Vast mountain sect gate with floating palaces disciples in robes amidst immortal mist clouds, grand scale epic xianxia golden-immortal-mist',
    '流浪地球': 'Sci-fi epic planet Earth with massive planetary thrusters attached, frozen wasteland landscape dying red sun distant sky, cinematic blue-white sci-fi movie poster',
    '三体': 'Hard science fiction three suns in alien sky over mysterious civilization ruin, dark space three red suns minimalist futuristic ominous red-dark-blue',
    '吞噬星空': 'Futuristic sci-fi warrior in powered armor absorbing cosmic energy from black hole stars galaxies swirling, epic space opera deep blue-purple-gold energy',
    '诡秘之主': 'Mysterious gentleman in victorian steampunk attire holding pocket watch gears floating, gothic clock tower foggy london street supernatural sepia-bronze',
    '大道朝天': 'Ascetic taoist immortal standing on cloud path leading to heavenly gates, ethereal light mountain peaks philosophical cultivation white-gold-celestial',
    '将夜': 'Young scholar with sword hidden in book box walking snow-covered imperial capital lantern-lit streets dusk, wuxia-literary fusion cold blue-warm orange',
    '牧神记': 'Young man with divine eyes seeing through reality layers multiple transparent worlds overlapping gods demons background mystical multi-layered colors',
    '全球高武': 'Modern martial artist sportswear performing impossible high kick energy shockwave city skyline background urban martial arts action dynamic blue-gold',
    '求魔': 'Tragic cultivation protagonist standing between two worlds light and darkness torn fate theme dual-toned half-light-half-dark emotional dark fantasy',
}

DEFAULT = 'epic chinese fantasy novel book cover, dramatic cinematic lighting, professional illustration, rich detailed artwork'

updated = 0
for novel in Novel.objects.all().order_by('id'):
    prompt = PROMPTS.get(novel.title, DEFAULT)
    url = f'{API}?prompt={quote(prompt)}&image_size={SIZE}'
    novel.cover = url
    novel.save(update_fields=['cover'])
    updated += 1
    print(f'  OK [{novel.id}] {novel.title}')

print(f'\nDone! {updated} covers restored to dynamic API URLs.')
print('NOTE: These URLs generate images in real-time via text_to_image API.')
print('      In Trae IDE browser context, they render as beautiful AI artwork.')
