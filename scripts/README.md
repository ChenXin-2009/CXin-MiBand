# 数据库分析与优化脚本

这个目录包含用于分析和优化词典数据库的开发脚本。这些脚本主要用于 vocabulary-app 的数据准备和优化工作。

## 📁 目录说明

### 分析脚本
- `analyze-db.js` - 基础数据库分析
- `analyze-db-detailed.js` - 详细分析报告
- `analyze-db-indexes.js` - 索引分析
- `analyze-db-size.js` - 体积分析
- `calculate-max-words.js` - 计算最大词汇量
- `precise-calculation.js` / `precise_calculation.py` - 精确计算

### 数据库创建脚本
- `create_optimized_db.py` - 创建优化数据库（第一版）
- `create_optimized_db_v2.py` - 创建优化数据库（第二版，推荐）
- `create_binary_dict.py` - 创建二进制格式词典
- `create_mini_dict.py` - 创建迷你词典
- `create_split_dict.py` - 创建分割词典
- `convert_db_to_json.py` - 数据库转JSON格式

### 查询和测试脚本
- `query_dict.py` - 查询词典
- `interactive_query.py` - 交互式查询（第一版）
- `interactive_query_v2.py` - 交互式查询（第二版，推荐）
- `test_binary_dict.py` - 测试二进制词典
- `test_compression.py` - 测试压缩效果
- `test_query.py` - 测试查询功能
- `why_800mb.py` - 分析800MB体积原因

### 文档
- `README.md` - 本文件
- `30MB_CAPACITY_ANALYSIS.md` - 30MB容量分析
- `FINAL_ANSWER.md` - 最终方案
- `FORMAT_COMPARISON.md` - 格式对比
- `FORMAT_SUMMARY.md` - 格式总结
- `OPTIMIZATION_FOR_WATCH.md` - 手表优化方案
- `SUMMARY.md` - 总结
- `USAGE.md` - 使用说明
- `WHY_800MB.md` - 为什么是800MB
- `WHY_BINARY_IS_BEST.md` - 为什么二进制格式最好

## 🎯 主要用途

这些脚本用于：
1. 分析原始 ECDICT 数据库（811MB）
2. 优化数据结构和索引
3. 筛选核心词汇（从340万词条减少到2万）
4. 转换为适合手环的格式
5. 测试不同格式的性能和体积

## 📊 优化成果

| 格式 | 文件大小 | 查询速度 | 推荐度 |
|------|---------|---------|--------|
| 原始SQLite | 811.85 MB | 快 | ❌ 太大 |
| 优化SQLite | 5.21 MB | < 1ms | ⭐⭐⭐⭐⭐ |
| 二进制格式 | 4.16 MB | < 5ms | ⭐⭐⭐⭐⭐ |
| JSON | 7.53 MB | < 100ms | ⭐⭐ |
| JSON.GZ | 1.96 MB | 慢 | ⭐⭐ |

## 🚀 快速使用

### 创建优化数据库
```bash
python scripts/create_optimized_db_v2.py
```

### 生成二进制格式（推荐）
```bash
python scripts/create_binary_dict.py
```

### 交互式查询测试
```bash
python scripts/interactive_query_v2.py
```

## ⚠️ 注意事项

1. **原始数据库**：需要先下载 ECDICT 数据库放在 `assets/ecdict-sqlite-28/` 目录
2. **Python环境**：需要 Python 3.6+ 和 sqlite3 模块
3. **Node.js环境**：JavaScript 脚本需要 Node.js 14+
4. **临时文件**：生成的临时文件会放在 `temp/` 目录

## 📚 相关文档

详细的分析报告和优化方案请查看目录中的 Markdown 文档。

---

**注意**：这些脚本主要用于开发阶段的数据准备工作，普通用户不需要运行这些脚本。
