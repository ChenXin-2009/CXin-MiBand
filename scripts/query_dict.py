#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'temp', 'optimized_dict.db')

def query_words(prefix, limit=20):
    """查询以指定前缀开头的单词"""
    if not os.path.exists(DB_PATH):
        print(f'错误: 数据库不存在: {DB_PATH}')
        print('请先运行: python scripts/create_optimized_db.py')
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 查询
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
        LIMIT ?
    ''', (prefix + '%', limit))
    
    results = cursor.fetchall()
    conn.close()
    
    return results

def display_results(results, prefix):
    """显示查询结果"""
    if not results:
        print(f'\n没有找到以 "{prefix}" 开头的单词\n')
        return
    
    print(f'\n找到 {len(results)} 个以 "{prefix}" 开头的单词:\n')
    print('=' * 80)
    
    for i, (word, phonetic, translation, collins, oxford) in enumerate(results, 1):
        # 标题行
        tags = []
        if oxford > 0:
            tags.append('⭐牛津')
        if collins > 0:
            tags.append(f'{"★" * collins}柯林斯')
        
        tag_str = f' [{", ".join(tags)}]' if tags else ''
        
        print(f'\n{i}. {word}{tag_str}')
        
        # 音标
        if phonetic:
            print(f'   /{phonetic}/')
        
        # 翻译
        print(f'   {translation}')
    
    print('\n' + '=' * 80 + '\n')

def get_word_detail(word):
    """获取单词详细信息"""
    if not os.path.exists(DB_PATH):
        print(f'错误: 数据库不存在')
        return None
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT word, phonetic, translation, collins, oxford
        FROM dict
        WHERE word = ? COLLATE NOCASE
    ''', (word,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result

def display_word_detail(word_info):
    """显示单词详细信息"""
    if not word_info:
        print('\n未找到该单词\n')
        return
    
    word, phonetic, translation, collins, oxford = word_info
    
    print('\n' + '=' * 80)
    print(f'\n单词: {word}')
    
    if phonetic:
        print(f'音标: /{phonetic}/')
    
    print(f'\n释义:')
    print(f'{translation}')
    
    print(f'\n标签:')
    if oxford > 0:
        print('  ⭐ 牛津3000核心词汇')
    if collins > 0:
        print(f'  {"★" * collins} 柯林斯{collins}星词汇')
    if not oxford and not collins:
        print('  高频词汇')
    
    print('\n' + '=' * 80 + '\n')

def interactive_mode():
    """交互式查询模式"""
    print('=' * 80)
    print('                        英语词典查询工具')
    print('=' * 80)
    print()
    print('使用说明:')
    print('  1. 输入字母查询以该字母开头的单词 (如: app)')
    print('  2. 输入 ":" + 单词查看详细信息 (如: :apple)')
    print('  3. 输入 "q" 或 "quit" 退出')
    print('  4. 输入 "?" 或 "help" 查看帮助')
    print()
    print('=' * 80)
    print()
    
    # 检查数据库
    if not os.path.exists(DB_PATH):
        print(f'错误: 数据库不存在: {DB_PATH}')
        print('请先运行: python scripts/create_optimized_db.py')
        return
    
    # 显示数据库信息
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM dict')
    total_words = cursor.fetchone()[0]
    file_size = os.path.getsize(DB_PATH) / 1024 / 1024
    conn.close()
    
    print(f'数据库: {total_words:,} 词条, {file_size:.2f} MB')
    print()
    
    while True:
        try:
            query = input('请输入查询 > ').strip()
            
            if not query:
                continue
            
            # 退出
            if query.lower() in ['q', 'quit', 'exit']:
                print('\n再见！\n')
                break
            
            # 帮助
            if query in ['?', 'help']:
                print('\n使用说明:')
                print('  输入字母: 查询以该字母开头的单词')
                print('  :单词: 查看单词详细信息')
                print('  q/quit: 退出程序')
                print()
                continue
            
            # 详细查询
            if query.startswith(':'):
                word = query[1:].strip()
                if word:
                    word_info = get_word_detail(word)
                    display_word_detail(word_info)
                continue
            
            # 前缀查询
            results = query_words(query.lower(), limit=20)
            display_results(results, query)
            
            if results:
                print(f'提示: 输入 ":单词" 查看详细信息，如 ":{results[0][0]}"')
                print()
        
        except KeyboardInterrupt:
            print('\n\n再见！\n')
            break
        except Exception as e:
            print(f'\n错误: {e}\n')

def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 命令行模式
        query = sys.argv[1].lower()
        
        if query.startswith(':'):
            # 详细查询
            word = query[1:]
            word_info = get_word_detail(word)
            display_word_detail(word_info)
        else:
            # 前缀查询
            results = query_words(query, limit=20)
            display_results(results, query)
    else:
        # 交互式模式
        interactive_mode()

if __name__ == '__main__':
    main()
