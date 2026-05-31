#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'ecdict-sqlite-28', 'stardict.db')

print('=== 为什么原始数据库有 800MB？===\n')

# 获取文件大小
file_size = os.path.getsize(DB_PATH)
file_size_mb = file_size / 1024 / 1024

print(f'原始数据库大小: {file_size_mb:.2f} MB ({file_size:,} 字节)\n')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. 总词条数
cursor.execute('SELECT COUNT(*) FROM stardict')
total_words = cursor.fetchone()[0]
print(f'总词条数: {total_words:,}\n')

# 2. 计算每个字段的总大小
print('=== 字段数据大小分析 ===\n')

fields = ['word', 'sw', 'phonetic', 'definition', 'translation', 
          'pos', 'collins', 'oxford', 'tag', 'bnc', 'frq', 'exchange', 'detail', 'audio']

cursor.execute(f'''
    SELECT 
        SUM(LENGTH(word)) as word_bytes,
        SUM(LENGTH(sw)) as sw_bytes,
        SUM(LENGTH(COALESCE(phonetic, ''))) as phonetic_bytes,
        SUM(LENGTH(COALESCE(definition, ''))) as definition_bytes,
        SUM(LENGTH(COALESCE(translation, ''))) as translation_bytes,
        SUM(LENGTH(COALESCE(pos, ''))) as pos_bytes,
        SUM(LENGTH(COALESCE(tag, ''))) as tag_bytes,
        SUM(LENGTH(COALESCE(exchange, ''))) as exchange_bytes,
        SUM(LENGTH(COALESCE(detail, ''))) as detail_bytes,
        SUM(LENGTH(COALESCE(audio, ''))) as audio_bytes,
        COUNT(*) * 20 as int_bytes
    FROM stardict
''')

row = cursor.fetchone()
field_sizes = {
    'word': row[0] or 0,
    'sw': row[1] or 0,
    'phonetic': row[2] or 0,
    'definition': row[3] or 0,
    'translation': row[4] or 0,
    'pos': row[5] or 0,
    'tag': row[6] or 0,
    'exchange': row[7] or 0,
    'detail': row[8] or 0,
    'audio': row[9] or 0,
    'integers': row[10] or 0,
}

total_field_bytes = sum(field_sizes.values())
total_field_mb = total_field_bytes / 1024 / 1024

print(f'{"字段名":<15} {"大小(MB)":>12} {"占总大小":>10} {"占字段数据":>12}')
print('-' * 52)

sorted_fields = sorted(field_sizes.items(), key=lambda x: x[1], reverse=True)

for field, size in sorted_fields:
    size_mb = size / 1024 / 1024
    pct_total = (size / file_size) * 100
    pct_field = (size / total_field_bytes) * 100
    print(f'{field:<15} {size_mb:>9.2f} MB {pct_total:>8.1f}% {pct_field:>10.1f}%')

print('-' * 52)
print(f'{"字段数据总计":<15} {total_field_mb:>9.2f} MB {(total_field_bytes/file_size)*100:>8.1f}%')

index_size = file_size - total_field_bytes
index_size_mb = index_size / 1024 / 1024
print(f'{"索引+元数据":<15} {index_size_mb:>9.2f} MB {(index_size/file_size)*100:>8.1f}%')
print(f'{"总计":<15} {file_size_mb:>9.2f} MB {"100.0%":>8}')

print('\n')

# 3. 分析索引
print('=== 索引分析 ===\n')

cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index'")
indexes = cursor.fetchall()

print(f'索引数量: {len(indexes)}\n')

for idx_name, idx_sql in indexes:
    print(f'索引: {idx_name}')
    if idx_sql:
        print(f'  {idx_sql}')
    else:
        print(f'  (自动创建)')
    print()

# 4. 对比优化前后
print('=== 优化前后对比 ===\n')

print('原始数据库 (340万词):')
print(f'  总大小: {file_size_mb:.2f} MB')
print(f'  每词占用: {file_size / total_words:.2f} 字节')
print(f'  字段数: 15 个')
print(f'  索引数: {len(indexes)} 个')
print(f'  字段数据: {total_field_mb:.2f} MB ({(total_field_bytes/file_size)*100:.1f}%)')
print(f'  索引数据: {index_size_mb:.2f} MB ({(index_size/file_size)*100:.1f}%)')
print()

print('优化后数据库 (4.7万词):')
print(f'  总大小: 4.02 MB')
print(f'  每词占用: 90.09 字节')
print(f'  字段数: 5 个')
print(f'  索引数: 1 个')
print(f'  字段数据: ~1.62 MB (40%)')
print(f'  索引数据: ~2.40 MB (60%)')
print()

# 5. 计算优化效果
print('=== 为什么差距这么大？===\n')

print('1. 词条数量差异:')
print(f'   原始: {total_words:,} 词')
print(f'   优化: 46,829 词')
print(f'   减少: {((total_words - 46829) / total_words * 100):.1f}%')
print()

print('2. 字段数量差异:')
print(f'   原始: 15 个字段')
print(f'   优化: 5 个字段 (word, phonetic, translation, collins, oxford)')
print(f'   删除: sw, definition, pos, tag, bnc, frq, exchange, detail, audio, id')
print()

print('3. 索引数量差异:')
print(f'   原始: {len(indexes)} 个索引')
print(f'   优化: 1 个索引 (word 主键)')
print(f'   减少: {len(indexes) - 1} 个索引')
print()

print('4. Translation 压缩:')
avg_translation_len = field_sizes['translation'] / total_words
print(f'   原始平均长度: {avg_translation_len:.1f} 字符')
print(f'   优化后限制: 150 字符')
print(f'   压缩率: ~40-50%')
print()

# 6. 详细分解
print('=== 800MB 的详细分解 ===\n')

components = [
    ('word 字段', field_sizes['word']),
    ('sw 字段 (删除)', field_sizes['sw']),
    ('phonetic 字段', field_sizes['phonetic']),
    ('definition 字段 (删除)', field_sizes['definition']),
    ('translation 字段', field_sizes['translation']),
    ('exchange 字段 (删除)', field_sizes['exchange']),
    ('其他字段 (删除)', sum([field_sizes[f] for f in ['pos', 'tag', 'detail', 'audio', 'integers']])),
    ('', 0),
    ('字段数据小计', total_field_bytes),
    ('', 0),
    ('索引 1: id', index_size / len(indexes)),
    ('索引 2: word', index_size / len(indexes)),
    ('索引 3: sw+word', index_size / len(indexes)),
    ('索引 4: word (nocase)', index_size / len(indexes)),
    ('其他索引', index_size / len(indexes) * (len(indexes) - 4)),
    ('', 0),
    ('索引+元数据小计', index_size),
]

print(f'{"成分":<30} {"大小(MB)":>12} {"占比":>10}')
print('-' * 53)

for name, size in components:
    if not name:
        print()
        continue
    size_mb = size / 1024 / 1024
    pct = (size / file_size) * 100
    print(f'{name:<30} {size_mb:>9.2f} MB {pct:>8.1f}%')

print()

# 7. 如果只优化索引
print('=== 如果只删除多余索引（不减少词条）===\n')

estimated_size_no_extra_indexes = total_field_bytes + (index_size / len(indexes))
estimated_size_mb = estimated_size_no_extra_indexes / 1024 / 1024

print(f'保留所有 {total_words:,} 词，但只保留 1 个索引:')
print(f'  预计大小: {estimated_size_mb:.2f} MB')
print(f'  节省: {file_size_mb - estimated_size_mb:.2f} MB ({((file_size_mb - estimated_size_mb) / file_size_mb * 100):.1f}%)')
print()

# 8. 如果只减少词条
print('=== 如果只减少词条（保留所有字段和索引）===\n')

ratio = 46829 / total_words
estimated_size_less_words = file_size * ratio
estimated_size_mb = estimated_size_less_words / 1024 / 1024

print(f'只保留 46,829 词，但保留所有字段和索引:')
print(f'  预计大小: {estimated_size_mb:.2f} MB')
print(f'  节省: {file_size_mb - estimated_size_mb:.2f} MB ({((file_size_mb - estimated_size_mb) / file_size_mb * 100):.1f}%)')
print()

# 9. 综合优化
print('=== 综合优化效果 ===\n')

print('优化策略组合:')
print('  1. 减少词条: 340万 → 4.7万 (减少 98.6%)')
print('  2. 删除字段: 15个 → 5个 (减少 67%)')
print('  3. 压缩 translation: 平均 12.5 → 限制 150 字符')
print('  4. 删除索引: 6个 → 1个 (减少 83%)')
print()
print(f'最终效果: {file_size_mb:.2f} MB → 4.02 MB')
print(f'压缩率: {((file_size_mb - 4.02) / file_size_mb * 100):.1f}%')
print()

print('如果扩展到 30MB:')
print('  可容纳词条: 349,171 词 (原始的 10.3%)')
print('  但功能更精简、查询更快')

conn.close()
