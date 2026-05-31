#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建迷你词典 - 只包含最常用的1000个单词
生成 JavaScript 格式，可以直接嵌入代码
"""

import sqlite3
import json
import os

# 数据库路径
DB_PATH = 'assets/ecdict-sqlite-28/stardict.db'
OUTPUT_JS = 'dict-app/src/utils/mini-dict-data.js'

def create_mini_dict():
    """创建迷你词典"""
    print('连接数据库...')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询最常用的1000个单词（按BNC词频排序）
    print('查询最常用的1000个单词...')
    cursor.execute('''
        SELECT word, phonetic, translation, pos, exchange, tag, bnc
        FROM stardict
        WHERE bnc > 0 AND bnc <= 1000
        ORDER BY bnc ASC
        LIMIT 1000
    ''')
    
    words = []
    for row in cursor.fetchall():
        word_data = {
            'word': row[0],
            'phonetic': row[1] or '',
            'translation': row[2] or '',
            'pos': row[3] or '',
            'exchange': row[4] or '',
            'tag': row[5] or '',
            'bnc': row[6] or 0
        }
        words.append(word_data)
    
    conn.close()
    
    print(f'找到 {len(words)} 个单词')
    
    # 按首字母分组
    print('按首字母分组...')
    grouped = {}
    for word_data in words:
        first_letter = word_data['word'][0].lower()
        if first_letter not in grouped:
            grouped[first_letter] = []
        grouped[first_letter].append(word_data)
    
    # 生成 JavaScript 代码
    print('生成 JavaScript 代码...')
    js_code = '''/**
 * 迷你词典数据 - 最常用的1000个单词
 * 自动生成，请勿手动编辑
 */

export const MINI_DICT_DATA = '''
    
    js_code += json.dumps(grouped, ensure_ascii=False, indent=2)
    js_code += ';\n\n'
    
    js_code += '''/**
 * 搜索单词
 * @param {string} prefix - 搜索前缀
 * @param {number} limit - 返回数量限制
 * @returns {Array} 匹配的单词列表
 */
export function searchMiniDict(prefix, limit = 10) {
  if (!prefix) return [];
  
  const lowerPrefix = prefix.toLowerCase();
  const firstLetter = lowerPrefix[0];
  
  const words = MINI_DICT_DATA[firstLetter] || [];
  const results = [];
  
  for (const word of words) {
    if (word.word.toLowerCase().startsWith(lowerPrefix)) {
      results.push(word);
      if (results.length >= limit) break;
    }
  }
  
  return results;
}
'''
    
    # 确保目录存在
    os.makedirs(os.path.dirname(OUTPUT_JS), exist_ok=True)
    
    # 写入文件
    print(f'写入文件: {OUTPUT_JS}')
    with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    # 计算文件大小
    file_size = os.path.getsize(OUTPUT_JS)
    print(f'文件大小: {file_size:,} 字节 ({file_size/1024:.2f} KB)')
    
    print('✅ 迷你词典创建完成！')
    print(f'   包含 {len(words)} 个单词')
    print(f'   覆盖 {len(grouped)} 个字母')
    print(f'   文件: {OUTPUT_JS}')

if __name__ == '__main__':
    create_mini_dict()
