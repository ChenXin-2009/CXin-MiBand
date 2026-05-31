#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交互式查询 V2 - 包含词性、词形变化、标签、词频
"""

import sqlite3
import os
import sys
import msvcrt

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'temp', 'optimized_dict_v2.db')

class DictQuery:
    def __init__(self):
        if not os.path.exists(DB_PATH):
            print(f'错误: 数据库不存在: {DB_PATH}')
            print('请先运行: python scripts/create_optimized_db_v2.py')
            sys.exit(1)
        
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.current_input = ""
        
        # 获取数据库信息
        self.cursor.execute('SELECT COUNT(*) FROM dict')
        self.total_words = self.cursor.fetchone()[0]
    
    def query(self, prefix, limit=10):
        """查询单词"""
        if not prefix:
            return []
        
        self.cursor.execute('''
            SELECT word, phonetic, translation, pos, exchange, tag, bnc
            FROM dict
            WHERE word LIKE ?
            ORDER BY 
                CASE 
                    WHEN bnc > 0 AND bnc <= 1000 THEN 1
                    WHEN bnc > 0 AND bnc <= 5000 THEN 2
                    WHEN bnc > 0 AND bnc <= 10000 THEN 3
                    WHEN bnc > 0 AND bnc <= 20000 THEN 4
                    ELSE 5
                END,
                LENGTH(word),
                word
            LIMIT ?
        ''', (prefix + '%', limit))
        
        return self.cursor.fetchall()
    
    def display_ui(self, results):
        """显示界面"""
        # 清屏
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 顶部标题
        print('=' * 80)
        print('                        英语词典 V2 - 手表模拟查询')
        print('=' * 80)
        print()
        
        # 输入区域
        print(f'当前输入: {self.current_input if self.current_input else "(空)"}')
        print('-' * 80)
        
        # 结果区域
        if not self.current_input:
            print('\n请输入字母开始查询...')
            print('\n提示:')
            print('  - 输入字母: 查询单词')
            print('  - Backspace: 删除最后一个字母')
            print('  - Enter: 查看第一个单词详情')
            print('  - ESC: 退出')
            print('\n新增功能:')
            print('  ✅ 词性标注 (n. v. adj. 等)')
            print('  ✅ 词形变化 (复数、过去式等)')
            print('  ✅ 词汇标签 (四级、六级、考研等)')
            print('  ✅ 词频排名 (BNC排名，越小越常用)')
        elif not results:
            print(f'\n没有找到以 "{self.current_input}" 开头的单词')
        else:
            print(f'\n找到 {len(results)} 个匹配的单词:\n')
            
            for i, (word, phonetic, translation, pos, exchange, tag, bnc) in enumerate(results, 1):
                # 词频标记
                freq_mark = ''
                if bnc > 0:
                    if bnc <= 1000:
                        freq_mark = '🔥'  # 超高频
                    elif bnc <= 5000:
                        freq_mark = '⭐'  # 高频
                    elif bnc <= 10000:
                        freq_mark = '✓'   # 常用
                
                # 音标
                phonetic_str = f' /{phonetic}/' if phonetic else ''
                
                # 词性
                pos_str = f' [{pos}]' if pos else ''
                
                # 翻译（截断）
                trans = translation[:45] + '...' if len(translation) > 45 else translation
                
                print(f'{i:2}. {word:<15}{phonetic_str:<20}{freq_mark}{pos_str}')
                print(f'    {trans}')
                
                # 标签
                if tag:
                    print(f'    标签: {tag}')
                
                print()
        
        # 底部提示
        print('-' * 80)
        print('标记: 🔥=超高频(Top1000) ⭐=高频(Top5000) ✓=常用(Top10000)')
        print('按键: [字母] 输入 | [Backspace] 删除 | [Enter] 详情 | [ESC] 退出')
        print('=' * 80)
    
    def show_detail(self, word_info):
        """显示单词详情"""
        if not word_info:
            return
        
        word, phonetic, translation, pos, exchange, tag, bnc = word_info
        
        # 清屏
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print('=' * 80)
        print('                            单词详情')
        print('=' * 80)
        print()
        
        print(f'单词: {word}')
        print()
        
        if phonetic:
            print(f'音标: /{phonetic}/')
            print()
        
        if pos:
            print(f'词性: {pos}')
            print()
        
        print('释义:')
        print(translation)
        print()
        
        if exchange:
            print('词形变化:')
            # 解析词形变化
            parts = exchange.split('/')
            for part in parts:
                if ':' in part:
                    code, forms = part.split(':', 1)
                    code_map = {
                        'p': '过去式',
                        'd': '过去分词',
                        'i': '现在分词',
                        '3': '第三人称单数',
                        'r': '比较级',
                        't': '最高级',
                        's': '复数',
                        '0': '原型',
                        '1': '变形'
                    }
                    code_name = code_map.get(code, code)
                    print(f'  {code_name}: {forms}')
            print()
        
        if tag:
            print(f'标签: {tag}')
            tag_map = {
                'zk': '中考',
                'gk': '高考',
                'cet4': '四级',
                'cet6': '六级',
                'ky': '考研',
                'gre': 'GRE',
                'toefl': '托福',
                'ielts': '雅思'
            }
            tags = tag.split()
            tag_names = [tag_map.get(t, t) for t in tags]
            print(f'  ({", ".join(tag_names)})')
            print()
        
        if bnc > 0:
            print(f'词频: BNC排名 {bnc:,}')
            if bnc <= 1000:
                print('  🔥 超高频词汇 (Top 1000)')
            elif bnc <= 5000:
                print('  ⭐ 高频词汇 (Top 5000)')
            elif bnc <= 10000:
                print('  ✓ 常用词汇 (Top 10000)')
            elif bnc <= 20000:
                print('  较常用词汇 (Top 20000)')
            print()
        
        print('=' * 80)
        print('按任意键返回...')
        
        # 等待按键
        msvcrt.getch()
    
    def run(self):
        """运行交互式查询"""
        results = []
        
        while True:
            # 显示界面
            self.display_ui(results)
            
            # 获取按键
            key = msvcrt.getch()
            
            # ESC 退出
            if key == b'\x1b':
                break
            
            # Backspace 删除
            elif key == b'\x08':
                if self.current_input:
                    self.current_input = self.current_input[:-1]
                    results = self.query(self.current_input) if self.current_input else []
            
            # Enter 查看详情
            elif key == b'\r':
                if results:
                    self.show_detail(results[0])
            
            # 字母或数字
            elif key.isalpha() or key.isdigit():
                char = key.decode('utf-8').lower()
                self.current_input += char
                results = self.query(self.current_input)
            
            # 空格清空
            elif key == b' ':
                self.current_input = ""
                results = []
        
        # 清屏并退出
        os.system('cls' if os.name == 'nt' else 'clear')
        print('\n再见！\n')
        
        self.conn.close()

def main():
    """主函数"""
    try:
        app = DictQuery()
        app.run()
    except KeyboardInterrupt:
        print('\n\n再见！\n')
    except Exception as e:
        print(f'\n错误: {e}\n')

if __name__ == '__main__':
    main()
