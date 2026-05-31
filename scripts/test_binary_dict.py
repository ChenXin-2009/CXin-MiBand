#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试二进制词典格式
验证数据的正确性和查询性能
"""

import struct
import os
import time

BIN_PATH = os.path.join(os.path.dirname(__file__), '..', 'dict-app', 'src', 'assets', 'dict.bin')

print('=== 测试二进制词典 ===\n')

# 检查文件
if not os.path.exists(BIN_PATH):
    print(f'❌ 错误: 文件不存在: {BIN_PATH}')
    exit(1)

# 读取文件
print('读取文件...')
with open(BIN_PATH, 'rb') as f:
    data = f.read()

file_size = len(data)
print(f'文件大小: {file_size / 1024 / 1024:.2f} MB\n')

# 解析文件头
print('=== 文件头 ===\n')
magic = data[0:4].decode('ascii')
version = struct.unpack('<H', data[4:6])[0]
total_words = struct.unpack('<I', data[6:10])[0]

print(f'Magic: {magic}')
print(f'Version: {version}')
print(f'Total Words: {total_words:,}')
print()

# 解析索引
print('=== 索引 ===\n')
index_start = 16
index = []

letters = [chr(i) for i in range(ord('a'), ord('z') + 1)] + ['#']

for i in range(27):
    offset_pos = index_start + i * 8
    offset = struct.unpack('<I', data[offset_pos:offset_pos+4])[0]
    count = struct.unpack('<I', data[offset_pos+4:offset_pos+8])[0]
    
    index.append({
        'letter': letters[i],
        'offset': offset,
        'count': count
    })
    
    if count > 0:
        print(f'{letters[i].upper()}: offset={offset}, count={count:,}')

print()

# 读取单词的函数
def read_word(offset):
    pos = offset
    
    # 读取单词
    word_len = data[pos]
    pos += 1
    word = data[pos:pos+word_len].decode('utf-8')
    pos += word_len
    
    # 读取音标
    phonetic_len = data[pos]
    pos += 1
    phonetic = data[pos:pos+phonetic_len].decode('utf-8') if phonetic_len > 0 else ''
    pos += phonetic_len
    
    # 读取翻译
    translation_len = struct.unpack('<H', data[pos:pos+2])[0]
    pos += 2
    translation = data[pos:pos+translation_len].decode('utf-8')
    pos += translation_len
    
    # 读取词性
    pos_len = data[pos]
    pos += 1
    pos_str = data[pos:pos+pos_len].decode('utf-8') if pos_len > 0 else ''
    pos += pos_len
    
    # 读取词形变化
    exchange_len = data[pos]
    pos += 1
    exchange = data[pos:pos+exchange_len].decode('utf-8') if exchange_len > 0 else ''
    pos += exchange_len
    
    # 读取标签
    tag_len = data[pos]
    pos += 1
    tag = data[pos:pos+tag_len].decode('utf-8') if tag_len > 0 else ''
    pos += tag_len
    
    # 读取 BNC
    bnc = struct.unpack('<I', data[pos:pos+4])[0]
    pos += 4
    
    return {
        'word': word,
        'phonetic': phonetic,
        'translation': translation,
        'pos': pos_str,
        'exchange': exchange,
        'tag': tag,
        'bnc': bnc,
        'next_offset': pos
    }

# 测试读取每个字母的第一个单词
print('=== 采样测试 (每个字母的第一个单词) ===\n')

for item in index:
    if item['count'] > 0:
        letter = item['letter']
        offset = item['offset']
        
        word_data = read_word(offset)
        
        print(f"{letter.upper()}: {word_data['word']}")
        if word_data['phonetic']:
            print(f"   音标: {word_data['phonetic']}")
        if word_data['pos']:
            print(f"   词性: {word_data['pos']}")
        print(f"   翻译: {word_data['translation'][:60]}...")
        if word_data['bnc'] > 0:
            print(f"   词频: {word_data['bnc']}")
        print()

# 性能测试：搜索功能
print('=== 性能测试 ===\n')

def search_words(prefix, limit=10):
    """搜索以指定前缀开头的单词"""
    prefix_lower = prefix.lower()
    first_letter = prefix_lower[0]
    
    # 找到对应的索引
    letter_index = ord(first_letter) - ord('a') if 'a' <= first_letter <= 'z' else 26
    
    if letter_index >= len(index):
        return []
    
    item = index[letter_index]
    if item['count'] == 0:
        return []
    
    results = []
    offset = item['offset']
    
    for i in range(item['count']):
        word_data = read_word(offset)
        
        if word_data['word'].lower().startswith(prefix_lower):
            results.append(word_data)
            if len(results) >= limit:
                break
        
        offset = word_data['next_offset']
    
    return results

# 测试用例
test_cases = [
    'a',
    'ap',
    'app',
    'appl',
    'apple',
    'hello',
    'world',
    'computer',
    'test',
    'python'
]

print('搜索测试:')
for test in test_cases:
    start_time = time.time()
    results = search_words(test, limit=10)
    end_time = time.time()
    
    elapsed_ms = (end_time - start_time) * 1000
    
    print(f'  "{test}": 找到 {len(results)} 个结果, 耗时 {elapsed_ms:.2f}ms')
    
    if results:
        for i, word in enumerate(results[:3], 1):
            freq_marker = ''
            if word['bnc'] > 0:
                if word['bnc'] <= 1000:
                    freq_marker = '🔥'
                elif word['bnc'] <= 5000:
                    freq_marker = '⭐'
                elif word['bnc'] <= 10000:
                    freq_marker = '✓'
            
            print(f'    {i}. {word["word"]} {freq_marker}')

print()

# 验证数据完整性
print('=== 数据完整性验证 ===\n')

total_read = 0
for item in index:
    total_read += item['count']

print(f'索引中的总词数: {total_read:,}')
print(f'文件头中的总词数: {total_words:,}')

if total_read == total_words:
    print('✅ 数据完整性验证通过')
else:
    print('❌ 数据完整性验证失败')

print()
print('=== 测试完成 ===')
