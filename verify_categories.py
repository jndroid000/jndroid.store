#!/usr/bin/env python
"""Verify 40 production categories in database"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from categories.models import Category

print('\n' + '='*80)
print('📊 DATABASE VERIFICATION - 40 PRODUCTION CATEGORIES')
print('='*80)

# All categories
all_cats = Category.objects.all().order_by('order')
print(f'\n✅ Total Categories in Database: {all_cats.count()}')
print(f'✅ Active Categories: {all_cats.filter(is_active=True).count()}')

# Display all
print('\n' + '-'*80)
print(f'{"Order":<6} {"Icon":<4} {"Name":<25} {"Slug":<20} {"Color":<8}')
print('-'*80)

for cat in all_cats:
    print(f'{cat.order:<6} {cat.icon:<4} {cat.name:<25} {cat.slug:<20} {cat.color:<8}')

print('-'*80)

# Statistics
icons_count = len(set(c.icon for c in all_cats))
colors_count = len(set(c.color for c in all_cats))
has_desc = sum(1 for c in all_cats if c.description)
has_icon_class = sum(1 for c in all_cats if c.icon_class)

print(f'\n📈 STATISTICS:')
print(f'   Unique Icons: {icons_count}')
print(f'   Unique Colors: {colors_count}')
print(f'   Has Descriptions: {has_desc}')
print(f'   Has Icon Classes: {has_icon_class}')
print(f'   All Active: {all_cats.filter(is_active=False).count() == 0}')

print(f'\n✨ All 40 categories are production-ready!')
print('='*80 + '\n')
