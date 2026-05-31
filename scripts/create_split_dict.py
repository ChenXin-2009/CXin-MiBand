#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建分割词典 - 按字母分组，每个字母一个文件
这样可以按需加载，减少初始加载时间
"""

import sqlite3
import json
import os

# 数据库路径
DB_PATH = 'assets/ecdict-sqlite-28/stardict.db'
OUTPUT_DIR = 'dict-app/src/utils/dict-data'

def create_split_dict():
    """创建分割词典"""
    print('连接数据库...')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 按字母分组查询
    letters = 'abcdefghijklmnopqrstuvwxyz'
    total_words = 0
    total_size = 0
    
    for letter in letters:
        print(f'处理字母 {letter.upper()}...')
        
        # 查询该字母开头的所有单词
        cursor.execute('''
            SELECT word, phonetic, translation, pos, exchange, tag, bnc
            FROM stardict
            WHERE word LIKE ? || '%'
            ORDER BY word ASC
        ''', (letter,))
        
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
        
        if len(words) == 0:
            print(f'  字母 {letter.upper()}: 0 个单词，跳过')
            continue
        
        # 生成 JavaScript 文件
        js_code = f'''/**
 * 词典数据 - 字母 {letter.upper()}
 * 包含 {len(words)} 个单词
 * 自动生成，请勿手动编辑
 */

export const DICT_DATA_{letter.upper()} = '''
        
        js_code += json.dumps(words, ensure_ascii=False, indent=2)
        js_code += ';\n'
        
        # 写入文件
        output_file = os.path.join(OUTPUT_DIR, f'dict-{letter}.js')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(js_code)
        
        file_size = os.path.getsize(output_file)
        total_words += len(words)
        total_size += file_size
        
        print(f'  字母 {letter.upper()}: {len(words)} 个单词, {file_size/1024:.2f} KB')
    
    conn.close()
    
    # 创建索引文件
    print('\n创建索引文件...')
    index_code = '''/**
 * 词典数据索引
 * 自动生成，请勿手动编辑
 */

// 动态导入函数
const dictModules = {
'''
    
    for letter in letters:
        index_code += f"  '{letter}': () => import('./dict-{letter}.js'),\n"
    
    index_code += '''};

// 缓存已加载的数据
const cache = {};

/**
 * 搜索单词
 * @param {string} prefix - 搜索前缀
 * @param {number} limit - 返回数量限制
 * @returns {Promise<Array>} 匹配的单词列表
 */
export async function searchDict(prefix, limit = 10) {
  if (!prefix) return [];
  
  const lowerPrefix = prefix.toLowerCase();
  const firstLetter = lowerPrefix[0];
  
  // 检查是否是有效字母
  if (!/[a-z]/.test(firstLetter)) return [];
  
  // 如果已缓存，直接使用
  if (cache[firstLetter]) {
    return searchInData(cache[firstLetter], lowerPrefix, limit);
  }
  
  // 动态加载数据
  try {
    const module = await dictModules[firstLetter]();
    const dataKey = `DICT_DATA_${firstLetter.toUpperCase()}`;
    cache[firstLetter] = module[dataKey];
    return searchInData(cache[firstLetter], lowerPrefix, limit);
  } catch (error) {
    console.error('加载词典数据失败:', error);
    return [];
  }
}

/**
 * 在数据中搜索
 */
function searchInData(data, prefix, limit) {
  const results = [];
  
  for (const word of data) {
    if (word.word.toLowerCase().startsWith(prefix)) {
      results.push(word);
      if (results.length >= limit) break;
    }
  }
  
  return results;
}
'''
    
    index_file = os.path.join(OUTPUT_DIR, 'index.js')
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_code)
    
    print(f'\n✅ 分割词典创建完成！')
    print(f'   总单词数: {total_words:,}')
    print(f'   总大小: {total_size/1024/1024:.2f} MB')
    print(f'   平均每个文件: {total_size/26/1024:.2f} KB')
    print(f'   输出目录: {OUTPUT_DIR}')

if __name__ == '__main__':
    create_split_dict()
