#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 SQLite 数据库转换为 JSON 格式
用于小米手环应用
"""

import sqlite3
import json
import os
import gzip

# 路径配置
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'temp', 'optimized_dict_v2.db')
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), '..', 'dict-app', 'src', 'assets', 'dict.json')
OUTPUT_JSON_GZ = os.path.join(os.path.dirname(__file__), '..', 'dict-app', 'src', 'assets', 'dict.json.gz')
ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'dict-app', 'src', 'assets')

# 确保目录存在
os.makedirs(ASSETS_DIR, exist_ok=True)

print('=== 转换数据库为 JSON ===\n')

# 检查数据库是否存在
if not os.path.exists(DB_PATH):
    print(f'❌ 错误: 数据库不存在')
    print(f'   路径: {DB_PATH}')
    print('\n请先运行: python scripts/create_optimized_db_v2.py')
    exit(1)

# 连接数据库
print('连接数据库...')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 查询所有数据
print('查询数据...')
cursor.execute('''
    SELECT word, phonetic, translation, pos, exchange, tag, bnc 
    FROM dict 
    ORDER BY word
''')

rows = cursor.fetchall()
print(f'找到 {len(rows):,} 个词条\n')

# 转换为 JSON 格式
print('转换为 JSON...')
data = []
for row in rows:
    word, phonetic, translation, pos, exchange, tag, bnc = row
    data.append({
        'word': word,
        'phonetic': phonetic or '',
        'translation': translation,
        'pos': pos or '',
        'exchange': exchange or '',
        'tag': tag or '',
        'bnc': bnc or 0
    })

conn.close()

# 写入 JSON 文件（紧凑格式）
print('写入 JSON 文件...')
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

json_size = os.path.getsize(OUTPUT_JSON)
json_size_mb = json_size / 1024 / 1024

print(f'✅ JSON 文件创建成功')
print(f'   路径: {OUTPUT_JSON}')
print(f'   大小: {json_size_mb:.2f} MB ({json_size:,} 字节)')
print(f'   词条: {len(data):,}')
print(f'   每词: {json_size / len(data):.2f} 字节')
print()

# 创建 GZIP 压缩版本
print('创建 GZIP 压缩版本...')
with open(OUTPUT_JSON, 'rb') as f_in:
    with gzip.open(OUTPUT_JSON_GZ, 'wb', compresslevel=9) as f_out:
        f_out.writelines(f_in)

gz_size = os.path.getsize(OUTPUT_JSON_GZ)
gz_size_mb = gz_size / 1024 / 1024
compression_ratio = (1 - gz_size / json_size) * 100

print(f'✅ GZIP 文件创建成功')
print(f'   路径: {OUTPUT_JSON_GZ}')
print(f'   大小: {gz_size_mb:.2f} MB ({gz_size:,} 字节)')
print(f'   压缩率: {compression_ratio:.1f}%')
print()

# 显示统计信息
print('=== 文件大小对比 ===\n')
db_size = os.path.getsize(DB_PATH)
db_size_mb = db_size / 1024 / 1024

print(f'SQLite 数据库: {db_size_mb:.2f} MB')
print(f'JSON 文件:     {json_size_mb:.2f} MB ({(json_size/db_size)*100:.1f}% of DB)')
print(f'JSON.GZ 文件:  {gz_size_mb:.2f} MB ({(gz_size/db_size)*100:.1f}% of DB)')
print()

# 建议
print('=== 使用建议 ===\n')
print('1. 如果手环支持 GZIP 解压，使用 dict.json.gz (更小)')
print('2. 如果不支持，使用 dict.json')
print('3. 如果手环支持 SQLite，直接使用数据库文件')
print()

# 采样显示
print('=== 数据采样 (前5个词) ===\n')
for i, item in enumerate(data[:5], 1):
    print(f'{i}. {item["word"]}')
    if item['phonetic']:
        print(f'   音标: {item["phonetic"]}')
    if item['pos']:
        print(f'   词性: {item["pos"]}')
    print(f'   翻译: {item["translation"][:60]}...')
    if item['bnc'] > 0:
        print(f'   词频: {item["bnc"]}')
    print()

print('转换完成！')
print(f'\n下一步: 在应用中加载 {os.path.basename(OUTPUT_JSON)}')
