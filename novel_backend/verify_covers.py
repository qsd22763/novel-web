import os, glob

cover_dir = 'media/covers'
files = sorted(glob.glob(os.path.join(cover_dir, 'cover_*.jpg')))
file_ids = set()
for f in files:
    name = os.path.basename(f)
    fid = name.replace('cover_', '').replace('.jpg', '')
    file_ids.add(int(fid))

print(f'封面文件总数: {len(files)}')

# 检查 88-165 范围内的 ID
missing_ids = []
for i in range(88, 166):
    if i not in file_ids:
        missing_ids.append(i)

print(f'ID范围 88-165 中缺失的封面: {missing_ids if missing_ids else "无"}')

# 检查所有文件大小和格式
tiny_files = []
gzip_files = []
ok_count = 0
for f in files:
    size = os.path.getsize(f)
    name = os.path.basename(f)
    if size < 500:
        tiny_files.append((name, size))
        continue
    with open(f, 'rb') as fp:
        header = fp.read(4).hex()
    if header.startswith('1f8b'):
        gzip_files.append((name, size))
    else:
        ok_count += 1

print(f'\n有效封面: {ok_count}')
if tiny_files:
    print(f'\n异常小文件(<500B): {len(tiny_files)}')
    for n, s in tiny_files:
        print(f'  {n}: {s}B')
if gzip_files:
    print(f'\nGZIP损坏文件: {len(gzip_files)}')
    for n, s in gzip_files:
        print(f'  {n}: {s}B (需要修复)')

if not tiny_files and not gzip_files:
    print('\n✓ 所有封面文件完整有效!')
