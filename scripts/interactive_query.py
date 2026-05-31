#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交互式查询 - 模拟手表输入体验
每输入一个字母，实时显示匹配的单词
"""

import sqlite3
import os
import sys
import msvcrt  # Windows 下获取按键

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'temp', 'optimized_dict.db')

class DictQuery:
    def __init__(self):
        if not os.path.exists(DB_PATH):
            print(f'错误: 数据库不存在: {DB_PATH}')
            print('请先运行: python scripts/create_optimized_db.py')
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
        
        return self.cursor.fetchall()
    
    def display_ui(self, results):
        """显示界面"""
        # 清屏
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 顶部标题
        print('=' * 80)
        print('                        英语词典 - 手表模拟查询')
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
        elif not results:
            print(f'\n没有找到以 "{self.current_input}" 开头的单词')
        else:
            print(f'\n找到 {len(results)} 个匹配的单词:\n')
            
            for i, (word, phonetic, translation, collins, oxford) in enumerate(results, 1):
                # 标签
                tags = []
                if oxford > 0:
                    tags.append('⭐')
                if collins >= 4:
                    tags.append('★' * collins)
                
                tag_str = ' ' + ''.join(tags) if tags else ''
                
                # 音标
                phonetic_str = f' /{phonetic}/' if phonetic else ''
                
                # 翻译（截断）
                trans = translation[:50] + '...' if len(translation) > 50 else translation
                
                print(f'{i:2}. {word:<15}{phonetic_str:<20}{tag_str}')
                print(f'    {trans}')
                print()
        
        # 底部提示
        print('-' * 80)
        print('按键: [字母] 输入 | [Backspace] 删除 | [Enter] 详情 | [ESC] 退出')
        print('=' * 80)
    
    def show_detail(self, word_info):
        """显示单词详情"""
        if not word_info:
            return
        
        word, phonetic, translation, collins, oxford = word_info
        
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
        
        print('释义:')
        print(translation)
        print()
        
        if oxford > 0 or collins > 0:
            print('标签:')
            if oxford > 0:
                print('  ⭐ 牛津3000核心词汇')
            if collins > 0:
                print(f'  {"★" * collins} 柯林斯{collins}星词汇')
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
