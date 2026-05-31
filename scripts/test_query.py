#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速测试脚本 - 演示查询功能
"""

import sqlite3
import os
import time

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'temp', 'optimized_dict.db')

def test_query(prefix):
    """测试查询性能和结果"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 计时
    start_time = time.time()
    
    cursor.execute('''
        SELECT word, phonetic, translation, collins, oxford
        FROM dict
        WHERE word LIKE ?
        ORDER BY 
            CASE 
                WHEN oxford > 0 THEN 1
                WHEN collins >= 4 THEN 2
                WHEN collins >= 2 THEN 3
                ELSE 4
            END,
            LENGTH(word),
            word
        LIMIT 20
    ''', (prefix + '%',))
    
    results = cursor.fetchall()
    query_time = (time.time() - start_time) * 1000  # 转换为毫秒
    
    conn.close()
    
    return results, query_time

def display_test_results(prefix, results, query_time):
    """显示测试结果"""
    print(f'\n查询: "{prefix}"')
    print(f'耗时: {query_time:.2f} ms')
    print(f'结果: {len(results)} 个单词')
    print('-' * 80)
    
    for i, (word, phonetic, translation, collins, oxford) in enumerate(results[:10], 1):
        tags = []
        if oxford > 0:
            tags.append('⭐')
        if collins >= 4:
            tags.append(f'{"★" * collins}')
        
        tag_str = ' ' + ''.join(tags) if tags else ''
        phonetic_str = f' /{phonetic}/' if phonetic else ''
        
        # 截断翻译
        trans = translation[:60] + '...' if len(translation) > 60 else translation
        
        print(f'{i:2}. {word:<15}{phonetic_str:<20}{tag_str}')
        print(f'    {trans}')

# 测试用例
test_cases = [
    'a',      # 单字母
    'app',    # 常用前缀
    'hello',  # 完整单词
    'comp',   # 技术词汇
    'inter',  # 长前缀
    'z',      # 少见字母
]

print('=' * 80)
print('                    词典查询性能测试')
print('=' * 80)

# 数据库信息
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM dict')
total_words = cursor.fetchone()[0]
file_size = os.path.getsize(DB_PATH) / 1024 / 1024
conn.close()

print(f'\n数据库: {total_words:,} 词条, {file_size:.2f} MB\n')

# 运行测试
for prefix in test_cases:
    results, query_time = test_query(prefix)
    display_test_results(prefix, results, query_time)
    print()

print('=' * 80)
print('\n测试完成！')
print('\n运行交互式查询: python scripts/query_dict.py')
print('或直接查询: python scripts/query_dict.py app')
print()
