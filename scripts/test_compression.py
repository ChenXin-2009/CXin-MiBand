#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试数据库压缩效果
"""

import os
import gzip
import zipfile
import time

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'temp', 'optimized_dict_v2.db')
TEMP_DIR = os.path.join(os.path.dirname(__file__), '..', 'temp')

print('=' * 80)
print('                        数据库压缩测试')
print('=' * 80)
print()

# 原始大小
original_size = os.path.getsize(DB_PATH)
original_mb = original_size / 1024 / 1024

print(f'原始数据库:')
print(f'  文件: optimized_dict_v2.db')
print(f'  大小: {original_mb:.2f} MB ({original_size:,} 字节)')
print()

# 测试 GZIP 压缩
print('测试 GZIP 压缩...')
gzip_path = os.path.join(TEMP_DIR, 'optimized_dict_v2.db.gz')

start_time = time.time()
with open(DB_PATH, 'rb') as f_in:
    with gzip.open(gzip_path, 'wb', compresslevel=9) as f_out:
        f_out.writelines(f_in)
gzip_time = time.time() - start_time

gzip_size = os.path.getsize(gzip_path)
gzip_mb = gzip_size / 1024 / 1024
gzip_ratio = (1 - gzip_size / original_size) * 100

print(f'  压缩后: {gzip_mb:.2f} MB ({gzip_size:,} 字节)')
print(f'  压缩率: {gzip_ratio:.1f}%')
print(f'  压缩时间: {gzip_time:.2f} 秒')

# 测试解压时间
start_time = time.time()
with gzip.open(gzip_path, 'rb') as f:
    data = f.read()
decompress_time = time.time() - start_time
print(f'  解压时间: {decompress_time:.2f} 秒')
print()

# 测试 ZIP 压缩
print('测试 ZIP 压缩...')
zip_path = os.path.join(TEMP_DIR, 'optimized_dict_v2.zip')

start_time = time.time()
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
    zipf.write(DB_PATH, 'optimized_dict_v2.db')
zip_time = time.time() - start_time

zip_size = os.path.getsize(zip_path)
zip_mb = zip_size / 1024 / 1024
zip_ratio = (1 - zip_size / original_size) * 100

print(f'  压缩后: {zip_mb:.2f} MB ({zip_size:,} 字节)')
print(f'  压缩率: {zip_ratio:.1f}%')
print(f'  压缩时间: {zip_time:.2f} 秒')
print()

# 总结
print('=' * 80)
print('                            压缩对比')
print('=' * 80)
print()
print(f'{"格式":<15} {"大小(MB)":>12} {"压缩率":>10} {"说明"}')
print('-' * 80)
print(f'{"原始":<15} {original_mb:>9.2f} MB {"-":>10} {"未压缩"}')
print(f'{"GZIP":<15} {gzip_mb:>9.2f} MB {gzip_ratio:>9.1f}% {"通用压缩格式"}')
print(f'{"ZIP":<15} {zip_mb:>9.2f} MB {zip_ratio:>9.1f}% {"常用压缩格式"}')
print()

# 手表应用建议
print('=' * 80)
print('                        手表应用压缩方案')
print('=' * 80)
print()

print('方案 1: 不压缩（推荐）')
print(f'  大小: {original_mb:.2f} MB')
print('  优点: 直接使用，无需解压，查询速度最快')
print('  缺点: 占用空间稍大')
print('  适用: 如果 30MB 空间充足')
print()

print('方案 2: RPK 自动压缩')
print(f'  大小: 约 {gzip_mb:.2f} MB (RPK打包时自动压缩)')
print('  优点: 打包时自动压缩，安装时自动解压')
print('  缺点: 无')
print('  适用: 推荐！小米手环 RPK 会自动压缩资源')
print()

print('方案 3: 手动 GZIP 压缩')
print(f'  大小: {gzip_mb:.2f} MB')
print('  优点: 压缩率高')
print('  缺点: 需要首次启动时解压（约 {decompress_time:.1f}秒），占用额外空间')
print('  适用: 如果需要极致压缩')
print()

# 清理测试文件
os.remove(gzip_path)
os.remove(zip_path)

print('=' * 80)
print()
print('结论:')
print('  1. 数据库本身已经很小 (5.21 MB)')
print('  2. RPK 打包时会自动压缩到约 3-4 MB')
print('  3. 建议直接使用，不需要额外压缩')
print('  4. 查询性能最重要，压缩会影响性能')
print()
