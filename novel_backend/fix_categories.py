# -*- coding: utf-8 -*-
"""统一分类数据：让BookCategory表名称与Novel.category字段值对齐"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')
import django; django.setup()
from novels.models import BookCategory, Novel

print("=== 修复前 ===")
for c in BookCategory.objects.filter(parent=None).order_by('sort_order', 'id'):
    print(f"  ID={c.id} name={c.name}")

# 1. "日韩" -> "玄幻" （39本小说用的就是这个名）
rihan = BookCategory.objects.filter(name='日韩').first()
if rihan:
    rihan.name = '玄幻'
    rihan.save(update_fields=['name'])
    print(f"\n  ID={rihan.id}: 日韩 -> 玄幻")

# 2. 子分类 "东方玄幻" 保持不变（已经是玄幻的子类）

# 3. 删除测试数据
test = BookCategory.objects.filter(name='测试验证分类')
if test.exists():
    tid = test.first().id
    test.delete()
    print(f"  已删除测试分类 ID={tid}")

# 4. 同时确认子分类也合理
print("\n=== 修复后 ===")
for c in BookCategory.objects.filter(parent=None).order_by('sort_order', 'id'):
    kids = list(c.children.all())
    kid_str = ', '.join(k.name for k in kids) if kids else '(无)'
    print(f"  ID={c.id} name={c.name} -> [{kid_str}]")

# 验证：所有小说的分类名都能在BookCategory中找到
print("\n=== 验证 ===")
from collections import Counter
novel_cats = set(Novel.objects.values_list('category', flat=True).distinct())
bc_names = set(BookCategory.objects.values_list('name', flat=True))
missing = novel_cats - bc_names
if missing:
    print(f"  ⚠️ 小说用了但分类表没有: {missing}")
else:
    print(f"  ✅ 全部 {len(novel_cats)} 种小说分类都在分类表中找到!")
print(f"  小说分类: {sorted(novel_cats)}")
print(f"  分类表:   {sorted(bc_names)}")
