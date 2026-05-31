#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import re
import time

# 路径配置
SOURCE_DB = os.path.join(os.path.dirname(__file__), '..', 'assets', 'ecdict-sqlite-28', 'stardict.db')
OUTPUT_DB = os.path.join(os.path.dirname(__file__), '..', 'temp', 'optimized_dict_v2.db')
TEMP_DIR = os.path.join(os.path.dirname(__file__), '..', 'temp')

# 确保目录存在
os.makedirs(TEMP_DIR, exist_ok=True)

print('=== 创建优化词典数据库 V2 ===\n')

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
    text = re.sub(r'\bprep\.\s*', '介 ', text)
    text = re.sub(r'\bconj\.\s*', '连 ', text)
    text = re.sub(r'\bpron\.\s*', '代 ', text)
    
    # 清理空格和换行
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 限制长度
    if len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0] + '...'
    
    return text

# 删除旧数据库
if os.path.exists(OUTPUT_DB):
    os.remove(OUTPUT_DB)
    print('已删除旧数据库\n')

# 连接数据库
print('连接源数据库...')
source_conn = sqlite3.connect(SOURCE_DB)
source_cursor = source_conn.cursor()

print('创建优化数据库...')
output_conn = sqlite3.connect(OUTPUT_DB)
output_cursor = output_conn.cursor()

# 创建优化的表结构
print('创建表结构...\n')
output_cursor.execute('''
    CREATE TABLE dict (
        word TEXT PRIMARY KEY COLLATE NOCASE,
        phonetic TEXT,
        translation TEXT,
        pos TEXT,
        exchange TEXT,
        tag TEXT,
        bnc INTEGER
    )
''')

# 词汇选择策略
print('=== 词汇选择策略 ===\n')
print('1. 牛津3000核心词汇')
print('2. 柯林斯1-5星词汇')
print('3. BNC前50000高频词')
print('4. 去重后的所有符合条件的词\n')

print('=== 新增字段 ===\n')
print('✅ pos - 词性（n. v. adj. 等）')
print('✅ exchange - 词形变化（复数、过去式等）')
print('✅ tag - 标签（四级、六级等）')
print('✅ bnc - BNC词频排名（数字越小越常用）')
print('❌ collins - 已删除')
print('❌ oxford - 已删除\n')

# 查询符合条件的词汇
print('查询符合条件的词汇...')
source_cursor.execute('''
    SELECT word, phonetic, translation, pos, exchange, tag, bnc
    FROM stardict
    WHERE oxford > 0 OR collins > 0 OR (bnc > 0 AND bnc <= 50000)
    ORDER BY 
        CASE 
            WHEN oxford > 0 THEN 1
            WHEN collins >= 4 THEN 2
            WHEN collins >= 2 THEN 3
            WHEN bnc <= 10000 THEN 4
            WHEN bnc <= 20000 THEN 5
            WHEN bnc <= 30000 THEN 6
            ELSE 7
        END,
        bnc ASC,
        word ASC
''')

print('开始处理和插入数据...\n')

inserted = 0
skipped = 0
start_time = time.time()

for row in source_cursor.fetchall():
    word, phonetic, translation, pos, exchange, tag, bnc = row
    
    # 跳过过长的词（可能是短语或专业术语）
    if len(word) > 50:
        skipped += 1
        continue
    
    # 压缩翻译
    translation = compress_translation(translation, max_length=150)
    
    # 如果翻译为空，跳过
    if not translation:
        skipped += 1
        continue
    
    try:
        output_cursor.execute('''
            INSERT INTO dict (word, phonetic, translation, pos, exchange, tag, bnc)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            word, 
            phonetic or '', 
            translation, 
            pos or '', 
            exchange or '', 
            tag or '', 
            bnc or 0
        ))
        
        inserted += 1
        
        # 每1000条显示进度
        if inserted % 1000 == 0:
            elapsed = time.time() - start_time
            rate = inserted / elapsed
            print(f'已插入: {inserted:,} 词 ({rate:.0f} 词/秒)', end='\r')
    
    except sqlite3.IntegrityError:
        # 重复的词，跳过
        skipped += 1
        continue

print(f'\n\n插入完成: {inserted:,} 词')
print(f'跳过: {skipped:,} 词\n')

# 提交事务
print('提交事务...')
output_conn.commit()

# VACUUM 压缩数据库
print('压缩数据库 (VACUUM)...')
output_cursor.execute('VACUUM')
output_conn.commit()

# 分析数据库
print('分析数据库 (ANALYZE)...')
output_cursor.execute('ANALYZE')
output_conn.commit()

# 关闭连接
source_conn.close()
output_conn.close()

# 获取文件大小
file_size = os.path.getsize(OUTPUT_DB)
file_size_mb = file_size / 1024 / 1024

print('\n=== 创建完成 ===\n')
print(f'数据库路径: {OUTPUT_DB}')
print(f'词条数: {inserted:,}')
print(f'文件大小: {file_size_mb:.2f} MB ({file_size:,} 字节)')
print(f'每词占用: {file_size / inserted:.2f} 字节')
print(f'占30MB比例: {(file_size_mb / 30) * 100:.1f}%')
print()

# 统计信息
print('=== 字段统计 ===\n')

conn = sqlite3.connect(OUTPUT_DB)
cursor = conn.cursor()

# 词性统计
cursor.execute("SELECT COUNT(*) FROM dict WHERE pos != ''")
pos_count = cursor.fetchone()[0]
print(f'有词性标注: {pos_count:,} ({(pos_count/inserted)*100:.1f}%)')

# 词形变化统计
cursor.execute("SELECT COUNT(*) FROM dict WHERE exchange != ''")
exchange_count = cursor.fetchone()[0]
print(f'有词形变化: {exchange_count:,} ({(exchange_count/inserted)*100:.1f}%)')

# 标签统计
cursor.execute("SELECT COUNT(*) FROM dict WHERE tag != ''")
tag_count = cursor.fetchone()[0]
print(f'有标签: {tag_count:,} ({(tag_count/inserted)*100:.1f}%)')

# BNC词频统计
cursor.execute("SELECT COUNT(*) FROM dict WHERE bnc > 0")
bnc_count = cursor.fetchone()[0]
print(f'有BNC词频: {bnc_count:,} ({(bnc_count/inserted)*100:.1f}%)')

# BNC词频分布
print('\nBNC词频分布:')
cursor.execute('''
    SELECT 
        CASE 
            WHEN bnc <= 1000 THEN 'Top 1000'
            WHEN bnc <= 5000 THEN 'Top 5000'
            WHEN bnc <= 10000 THEN 'Top 10000'
            WHEN bnc <= 20000 THEN 'Top 20000'
            WHEN bnc <= 50000 THEN 'Top 50000'
            ELSE '其他'
        END as range,
        COUNT(*) as count
    FROM dict
    WHERE bnc > 0
    GROUP BY range
    ORDER BY MIN(bnc)
''')

for row in cursor.fetchall():
    range_name, count = row
    percentage = (count / inserted) * 100
    print(f'  {range_name}: {count:,} ({percentage:.1f}%)')

# 词长分布
print('\n词长分布:')
cursor.execute('''
    SELECT 
        CASE 
            WHEN LENGTH(word) <= 5 THEN '1-5字符'
            WHEN LENGTH(word) <= 10 THEN '6-10字符'
            WHEN LENGTH(word) <= 15 THEN '11-15字符'
            ELSE '15+字符'
        END as length_range,
        COUNT(*) as count
    FROM dict
    GROUP BY length_range
    ORDER BY MIN(LENGTH(word))
''')

for row in cursor.fetchall():
    length_range, count = row
    percentage = (count / inserted) * 100
    print(f'  {length_range}: {count:,} ({percentage:.1f}%)')

# 采样显示
print('\n=== 随机采样 (10个词) ===\n')
cursor.execute('SELECT word, phonetic, translation, pos, exchange, tag, bnc FROM dict ORDER BY RANDOM() LIMIT 10')

for i, row in enumerate(cursor.fetchall(), 1):
    word, phonetic, translation, pos, exchange, tag, bnc = row
    print(f'{i}. {word}')
    if phonetic:
        print(f'   音标: {phonetic}')
    if pos:
        print(f'   词性: {pos}')
    print(f'   翻译: {translation[:80]}{"..." if len(translation) > 80 else ""}')
    if exchange:
        print(f'   词形: {exchange[:60]}{"..." if len(exchange) > 60 else ""}')
    if tag:
        print(f'   标签: {tag}')
    if bnc > 0:
        print(f'   词频: BNC排名 {bnc}')
    print()

conn.close()

print('数据库创建完成！')
print(f'\n运行 "python scripts/query_dict_v2.py" 来测试查询功能')
