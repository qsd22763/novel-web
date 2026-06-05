import os

COVER_DIR = r'd:\python damo\vue\novel_backend\media\covers'

print('Checking file headers for invalid content...\n')
for i in range(88, 166):
    fpath = os.path.join(COVER_DIR, f'cover_{i:02d}.jpg')
    if not os.path.exists(fpath):
        print(f'  [{i}] MISSING')
        continue
    with open(fpath, 'rb') as f:
        header = f.read(20)
    size = os.path.getsize(fpath)
    
    is_jpg = header[:3] == b'\xff\xd8\xff'
    is_png = header[:4] == b'\x89PNG'
    is_gif = header[:3] == b'GIF'
    is_html = b'<html' in header.lower() or b'<!DOCTYPE' in header.lower()
    is_svg = header[:5] == b'<?xml' or b'<svg' in header.lower()
    
    if is_jpg:
        pass  # OK
    elif is_png:
        print(f'  [{i}] PNG ({size}B) - not JPG!')
    elif is_html:
        print(f'  [{i}] HTML PAGE! ({size}B) - BROKEN')
    elif is_gif:
        print(f'  [{i}] GIF ({size}B)')
    elif is_svg:
        print(f'  [{i}] SVG ({size}B)')
    else:
        print(f'  [{i}] UNKNOWN format! header={header[:10].hex()} ({size}B)')
