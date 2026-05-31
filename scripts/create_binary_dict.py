#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建自定义二进制词典格式
专为小米手环优化：文件小、查询快、内存占用低
"""

import sqlite3
import struct
import os

# 路径配置
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'temp', 'optimized_dict_v2.db')
OUTPUT_BIN = os.path.join(os.path.dirname(__file__), '..', 'dict-app', 'src', 'assets', 'dict.bin')
ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'dict-app', 'src', 'assets')

# 确保目录存在
os.makedirs(ASSETS_DIR, exist_ok=True)

print('=== 创建二进制词典 ===\n')

# 检查数据库
if not os.path.exists(DB_PATH):
    print(f'❌ 错误: 数据库不存在: {DB_PATH}')
    exit(1)

# 连接数据库
print('连接数据库...')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 查询所有数据，按单词排序
print('查询数据...')
cursor.execute('''
    SELECT word, phonetic, translation, pos, exchange, tag, bnc 
    FROM dict 
    ORDER BY word COLLATE NOCASE
''')

rows = cursor.fetchall()
print(f'找到 {len(rows):,} 个词条\n')

# 按首字母分组
print('按首字母分组...')
letter_groups = {}
for row in rows:
    word = row[0].lower()
    first_letter = word[0] if word[0].isalpha() else '#'
    
    if first_letter not in letter_groups:
        letter_groups[first_letter] = []
    
    letter_groups[first_letter].append(row)

print(f'分为 {len(letter_groups)} 组\n')

# 创建二进制文件
print('创建二进制文件...')

with open(OUTPUT_BIN, 'wb') as f:
    # === 文件头 (Header) ===
    # Magic Number: "DICT" (4 bytes)
    f.write(b'DICT')
    
    # Version: 1 (2 bytes)
    f.write(struct.pack('<H', 1))
    
    # Total word count (4 bytes)
    f.write(struct.pack('<I', len(rows)))
    
    # Reserved (6 bytes) - 预留空间
    f.write(b'\x00' * 6)
    
    # === 索引区 (Index) ===
    # 记录索引区的起始位置
    index_start = f.tell()
    
    # 为每个字母预留索引空间 (27组: a-z + #)
    # 每组: offset (4 bytes) + count (4 bytes) = 8 bytes
    # 总共: 27 * 8 = 216 bytes
    index_placeholder = f.tell()
    f.write(b'\x00' * (27 * 8))
    
    # === 数据区 (Data) ===
    data_start = f.tell()
    
    # 记录每个字母组的偏移量和数量
    letter_index = {}
    
    # 按字母顺序写入数据
    letters = sorted(letter_groups.keys())
    
    for letter in letters:
        group = letter_groups[letter]
        
        # 记录这个字母组的起始位置
        group_offset = f.tell()
        group_count = len(group)
        
        letter_index[letter] = (group_offset, group_count)
        
        # 写入这个字母组的所有单词
        for row in group:
            word, phonetic, translation, pos, exchange, tag, bnc = row
            
            # 编码为 UTF-8
            word_bytes = word.encode('utf-8')
            phonetic_bytes = (phonetic or '').encode('utf-8')
            translation_bytes = translation.encode('utf-8')
            pos_bytes = (pos or '').encode('utf-8')
            exchange_bytes = (exchange or '').encode('utf-8')
            tag_bytes = (tag or '').encode('utf-8')
            
            # 写入单词长度和内容
            f.write(struct.pack('<B', len(word_bytes)))
            f.write(word_bytes)
            
            # 写入音标长度和内容
            f.write(struct.pack('<B', len(phonetic_bytes)))
            if phonetic_bytes:
                f.write(phonetic_bytes)
            
            # 写入翻译长度和内容 (使用2字节表示长度，支持更长的翻译)
            f.write(struct.pack('<H', len(translation_bytes)))
            f.write(translation_bytes)
            
            # 写入词性长度和内容
            f.write(struct.pack('<B', len(pos_bytes)))
            if pos_bytes:
                f.write(pos_bytes)
            
            # 写入词形变化长度和内容
            f.write(struct.pack('<B', len(exchange_bytes)))
            if exchange_bytes:
                f.write(exchange_bytes)
            
            # 写入标签长度和内容
            f.write(struct.pack('<B', len(tag_bytes)))
            if tag_bytes:
                f.write(tag_bytes)
            
            # 写入 BNC 词频 (4 bytes)
            f.write(struct.pack('<I', bnc or 0))
    
    # 回到索引区，写入实际的索引数据
    f.seek(index_placeholder)
    
    # 定义字母顺序 (a-z + #)
    all_letters = [chr(i) for i in range(ord('a'), ord('z') + 1)] + ['#']
    
    for letter in all_letters:
        if letter in letter_index:
            offset, count = letter_index[letter]
            f.write(struct.pack('<I', offset))
            f.write(struct.pack('<I', count))
        else:
            # 没有这个字母的单词
            f.write(struct.pack('<I', 0))
            f.write(struct.pack('<I', 0))

conn.close()

# 获取文件大小
file_size = os.path.getsize(OUTPUT_BIN)
file_size_mb = file_size / 1024 / 1024

print('\n=== 创建完成 ===\n')
print(f'文件路径: {OUTPUT_BIN}')
print(f'文件大小: {file_size_mb:.2f} MB ({file_size:,} 字节)')
print(f'词条数: {len(rows):,}')
print(f'每词占用: {file_size / len(rows):.2f} 字节')
print(f'占30MB比例: {(file_size_mb / 30) * 100:.1f}%')
print()

# 对比其他格式
print('=== 格式对比 ===\n')

db_path = DB_PATH
json_path = os.path.join(ASSETS_DIR, 'dict.json')
json_gz_path = os.path.join(ASSETS_DIR, 'dict.json.gz')

if os.path.exists(db_path):
    db_size = os.path.getsize(db_path) / 1024 / 1024
    print(f'SQLite:      {db_size:.2f} MB ({(file_size_mb/db_size)*100:.1f}%)')

if os.path.exists(json_path):
    json_size = os.path.getsize(json_path) / 1024 / 1024
    print(f'JSON:        {json_size:.2f} MB ({(file_size_mb/json_size)*100:.1f}%)')

if os.path.exists(json_gz_path):
    json_gz_size = os.path.getsize(json_gz_path) / 1024 / 1024
    print(f'JSON.GZ:     {json_gz_size:.2f} MB ({(file_size_mb/json_gz_size)*100:.1f}%)')

print(f'Binary:      {file_size_mb:.2f} MB (100%)')
print()

# 显示索引信息
print('=== 索引信息 ===\n')
print(f'索引组数: {len(letter_groups)}')
print(f'索引大小: 216 字节')
print()

# 显示每个字母的统计
print('字母分布:')
for letter in sorted(letter_groups.keys()):
    count = len(letter_groups[letter])
    percentage = (count / len(rows)) * 100
    print(f'  {letter.upper()}: {count:,} 词 ({percentage:.1f}%)')

print()
print('✅ 二进制词典创建完成！')
print()
print('优势:')
print('  1. 文件小 - 比 JSON 小 50%+')
print('  2. 查询快 - 直接跳转到对应字母区域')
print('  3. 内存低 - 只加载需要的部分')
print('  4. 无依赖 - 不需要第三方库')
print()
print('下一步: 实现 JavaScript 解码器')
