#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import re
import time
import random

# 路径配置
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'ecdict-sqlite-28', 'stardict.db')
TEMP_DIR = os.path.join(os.path.dirname(__file__), '..', 'temp')

TARGET_SIZE_MB = 30
TARGET_SIZE_BYTES = TARGET_SIZE_MB * 1024 * 1024

print('=== 精确计算 30MB 可容纳词条数 ===\n')
print(f'目标大小: {TARGET_SIZE_MB} MB = {TARGET_SIZE_BYTES:,} 字节\n')

# 确保 temp 目录存在
os.makedirs(TEMP_DIR, exist_ok=True)

def compress_translation(text, max_length=150):
    """压缩翻译内容"""
    if not text:
        return ''
    
    # 删除标记
    text = re.sub(r'\[网络\][^\n]*', '', text)
    text = re.sub(r'\[地名\][^\n]*', '', text)
    text = re.sub(r'\[人名\][^\n]*', '', text)
    
    # 简化词性标记
    text = re.sub(r'\bna\.\s*', '', text)
    text = re.sub(r'\bn\.\s*', '名 ', text)
    text = re.sub(r'\bv\.\s*', '动 ', text)
    text = re.sub(r'\badj\.\s*', '形 ', text)
    text = re.sub(r'\badv\.\s*', '副 ', text)
    
    # 清理空格
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 限制长度
    return text[:max_length]

def create_test_db(word_count, compression_level=150):
    """创建测试数据库"""
    # 使用唯一的文件名
    temp_db_path = os.path.join(TEMP_DIR, f'test_{word_count}_{int(time.time())}.db')
    
    # 连接源数据库
    source_conn = sqlite3.connect(DB_PATH)
    source_cursor = source_conn.cursor()
    
    # 创建测试数据库
    test_conn = sqlite3.connect(temp_db_path)
    test_cursor = test_conn.cursor()
    
    # 创建表结构
    test_cursor.execute('''
        CREATE TABLE dict (
            word TEXT PRIMARY KEY COLLATE NOCASE,
            phonetic TEXT,
            translation TEXT,
            collins INTEGER DEFAULT 0,
            oxford INTEGER DEFAULT 0
        )
    ''')
    
    # 查询数据
    source_cursor.execute(f'''
        SELECT word, phonetic, translation, collins, oxford
        FROM stardict
        WHERE oxford > 0 OR collins > 0 OR (bnc > 0 AND bnc <= 50000)
        LIMIT {word_count}
    ''')
    
    # 插入数据
    rows_inserted = 0
    for row in source_cursor.fetchall():
        word, phonetic, translation, collins, oxford = row
        
        # 压缩翻译
        translation = compress_translation(translation, compression_level)
        
        test_cursor.execute('''
            INSERT INTO dict (word, phonetic, translation, collins, oxford)
            VALUES (?, ?, ?, ?, ?)
        ''', (word, phonetic, translation, collins or 0, oxford or 0))
        
        rows_inserted += 1
    
    test_conn.commit()
    
    # VACUUM 压缩
    test_cursor.execute('VACUUM')
    test_conn.commit()
    
    # 关闭连接
    test_conn.close()
    source_conn.close()
    
    # 获取文件大小
    file_size = os.path.getsize(temp_db_path)
    
    return file_size, rows_inserted, temp_db_path

def analyze_components(word_count, db_path):
    """分析数据库成分"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            SUM(LENGTH(word)) as word_bytes,
            SUM(LENGTH(COALESCE(phonetic, ''))) as phonetic_bytes,
            SUM(LENGTH(COALESCE(translation, ''))) as translation_bytes,
            COUNT(*) as count
        FROM dict
    ''')
    
    row = cursor.fetchone()
    word_bytes = row[0] or 0
    phonetic_bytes = row[1] or 0
    translation_bytes = row[2] or 0
    count = row[3] or 0
    
    # 整数字段 (collins + oxford)
    int_bytes = count * 8
    
    conn.close()
    
    return {
        'word': word_bytes,
        'phonetic': phonetic_bytes,
        'translation': translation_bytes,
        'integers': int_bytes,
        'count': count
    }

# 测试不同词条数
test_sizes = [1000, 5000, 10000, 20000, 30000, 50000]
results = []
test_db_files = []

print('正在创建测试数据库，精确测量实际大小...\n')

for test_size in test_sizes:
    print(f'测试 {test_size:,} 词条...')
    
    file_size, rows, db_path = create_test_db(test_size, compression_level=150)
    test_db_files.append(db_path)
    size_mb = file_size / 1024 / 1024
    bytes_per_word = file_size / rows
    percentage = (file_size / TARGET_SIZE_BYTES) * 100
    
    print(f'  实际大小: {size_mb:.2f} MB ({file_size:,} 字节)')
    print(f'  每词占用: {bytes_per_word:.2f} 字节')
    print(f'  占用率: {percentage:.1f}%\n')
    
    results.append({
        'words': rows,
        'bytes': file_size,
        'size_mb': size_mb,
        'bytes_per_word': bytes_per_word,
        'percentage': percentage,
        'db_path': db_path
    })

# 显示结果表格
print('=== 实际测试结果 ===\n')
print(f'{"词条数":<12} {"数据库大小":>15} {"每词占用":>12} {"占用率":>10}')
print('-' * 50)

for r in results:
    print(f'{r["words"]:<12,} {r["size_mb"]:>12.2f} MB {r["bytes_per_word"]:>9.2f} B {r["percentage"]:>8.1f}%')

print('-' * 50)
print(f'目标限制: {TARGET_SIZE_MB} MB\n')

# 分析 50000 词的成分
print('=== 数据库成分分析 ===\n')

result_50k = next((r for r in results if r['words'] == 50000), None)

if result_50k:
    components = analyze_components(50000, result_50k['db_path'])
    
    total_data_bytes = (components['word'] + components['phonetic'] + 
                       components['translation'] + components['integers'])
    total_db_bytes = result_50k['bytes']
    index_bytes = total_db_bytes - total_data_bytes
    
    print(f'基于 50,000 词的数据库 ({result_50k["size_mb"]:.2f} MB)：\n')
    print(f'{"字段名":<20} {"大小(MB)":>12} {"占比":>10}')
    print('-' * 43)
    
    items = [
        ('word 字段', components['word']),
        ('phonetic 字段', components['phonetic']),
        ('translation 字段', components['translation']),
        ('collins+oxford', components['integers']),
        ('', 0),  # 空行
        ('小计(字段数据)', total_data_bytes),
        ('索引+元数据', index_bytes),
        ('', 0),  # 空行
        ('总计', total_db_bytes),
    ]
    
    for name, byte_size in items:
        if not name:
            print()
            continue
        mb = byte_size / 1024 / 1024
        percentage = (byte_size / total_db_bytes) * 100
        print(f'{name:<20} {mb:>9.2f} MB {percentage:>8.1f}%')
    
    print('\n关键发现：')
    print(f'- 字段数据占 {(total_data_bytes / total_db_bytes) * 100:.1f}%')
    print(f'- 索引+元数据占 {(index_bytes / total_db_bytes) * 100:.1f}%')
    print(f'- Translation 占字段数据的 {(components["translation"] / total_data_bytes) * 100:.1f}%')
    print(f'- 平均 translation 长度: {components["translation"] / components["count"]:.1f} 字符\n')

# 容量计算
print('=== 容量计算 ===\n')

# 使用最大的测试结果
largest_result = results[-1]
avg_bytes = largest_result['bytes_per_word']

print(f'基于 {largest_result["words"]:,} 词的测试：')
print(f'平均每词占用: {avg_bytes:.2f} 字节\n')

# 不同压缩策略
compression_levels = [
    ('当前压缩(150字符)', 1.0),
    ('轻度压缩(200字符)', 1.15),
    ('重度压缩(100字符)', 0.85),
    ('极限压缩(50字符)', 0.70),
]

print('不同压缩策略下的最大词条数：\n')
print(f'{"压缩策略":<25} {"每词占用":>12} {"最大词条数":>15} {"实际大小":>12}')
print('-' * 65)

for name, factor in compression_levels:
    bytes_per_word = avg_bytes * factor
    max_words = int(TARGET_SIZE_BYTES / bytes_per_word)
    actual_size_mb = (max_words * bytes_per_word) / 1024 / 1024
    
    print(f'{name:<25} {bytes_per_word:>9.1f} B {max_words:>15,} {actual_size_mb:>9.2f} MB')

print()

# 与其他词典对比
print('=== 与其他词典对比 ===\n')

print('其他人的词典: 4 MB = 50,000 词')
print('计算: 4 MB / 50,000 = 81.92 字节/词\n')

largest_result = results[-1]
print(f'你的数据库: {largest_result["size_mb"]:.2f} MB = {largest_result["words"]:,} 词')
print(f'计算: {largest_result["size_mb"]:.2f} MB / {largest_result["words"]:,} = {largest_result["bytes_per_word"]:.2f} 字节/词\n')

if largest_result['bytes_per_word'] > 82:
    diff = largest_result['bytes_per_word'] - 81.92
    print(f'⚠️  你的数据库每词多占用 {diff:.2f} 字节 (+{(diff/81.92*100):.1f}%)，可能原因：')
    print('1. Translation 字段更长（更详细的翻译）')
    print('2. 包含 phonetic 字段（其他词典可能没有）')
    print('3. 包含 collins 和 oxford 标记')
    print('4. SQLite 索引开销\n')
else:
    print('✅ 你的数据库已经很优化了！\n')

# 30MB 容量计算
print('=== 30MB 容量计算 ===\n')

largest_result = results[-1]
bytes_per_word = largest_result['bytes_per_word']
max_words = int(TARGET_SIZE_BYTES / bytes_per_word)

print(f'基于实测数据 ({bytes_per_word:.2f} 字节/词)：')
print(f'30 MB 可容纳: {max_words:,} 词')
print(f'实际大小: {(max_words * bytes_per_word / 1024 / 1024):.2f} MB\n')

# 如果优化到其他词典水平
others_max_words = int(TARGET_SIZE_BYTES / 81.92)
print(f'如果优化到其他词典水平 (81.92 字节/词)：')
print(f'30 MB 可容纳: {others_max_words:,} 词')
print(f'实际大小: {(others_max_words * 81.92 / 1024 / 1024):.2f} MB\n')

# 推荐方案
print('=== 推荐方案 ===\n')

largest_result = results[-1]
# 计算不同词汇量方案
scenarios = [
    ('方案A: 最大化', 0.85, '重度压缩(100字符)'),
    ('方案B: 平衡', 1.0, '中度压缩(150字符)'),
    ('方案C: 保守', 1.15, '轻度压缩(200字符)'),
]

for name, factor, desc in scenarios:
    bytes_pw = largest_result['bytes_per_word'] * factor
    max_w = int(TARGET_SIZE_BYTES / bytes_pw)
    size = (max_w * bytes_pw) / 1024 / 1024
    
    print(f'{name}')
    print(f'  压缩策略: {desc}')
    print(f'  最大词条: {max_w:,} 词')
    print(f'  数据库大小: {size:.2f} MB')
    print(f'  剩余空间: {TARGET_SIZE_MB - size:.2f} MB')
    print()

print('测试完成！')

# 清理测试文件
for db_file in test_db_files:
    try:
        if os.path.exists(db_file):
            os.remove(db_file)
    except:
        pass
