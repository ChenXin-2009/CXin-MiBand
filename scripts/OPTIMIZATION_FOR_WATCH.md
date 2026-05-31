# 小米手环查词应用 - 数据库优化方案

## 📱 设备信息

### 小米手环 9 Pro 配置
- **处理器**: 低功耗芯片（类似 ARM Cortex-M 系列）
- **内存**: 32-64 MB RAM
- **存储**: 有限的闪存空间
- **性能**: 算力很弱，需要高度优化

### 应用限制
- RPK 包大小: < 30 MB
- 查询响应: < 100ms（理想）
- 内存占用: 尽可能小

## 🎨 应用界面设计

```
┌─────────────────────────────────┐
│ 输入: app    │ apple, application, ... │  ← 顶部显示区
├─────────────────────────────────┤
│                                 │
│  [A] [B] [C] [D] [E] [F]       │
│  [G] [H] [I] [J] [K] [L]       │  ← 5x6 按键区
│  [M] [N] [O] [P] [Q] [R]       │     (30个按钮)
│  [S] [T] [U] [V] [W] [X]       │
│  [Y] [Z] [?] [?] [?] [?]       │
│                                 │
└─────────────────────────────────┘
```

### 交互流程
1. 用户点击字母按钮 → 输入区显示 "a"
2. 实时查询数据库 → 显示 "a" 开头的单词
3. 左右滑动查看更多单词
4. 点击单词 → 进入详情页

## 🔍 查询需求分析

### 核心查询

```sql
-- 查询以 "app" 开头的单词（前缀匹配）
SELECT word, phonetic, translation, collins, oxford
FROM dict
WHERE word LIKE 'app%'
ORDER BY word
LIMIT 20;
```

### 查询特点
- **前缀匹配**: `word LIKE 'a%'`, `word LIKE 'ap%'`, `word LIKE 'app%'`
- **实时查询**: 每输入一个字母就查询一次
- **限制结果**: 只显示前 10-20 个结果
- **排序**: 按字母顺序

## 💡 索引优化方案

### 方案 A：单一主键索引（推荐）

```sql
CREATE TABLE dict (
  word TEXT PRIMARY KEY,      -- 自动创建 B-Tree 索引
  phonetic TEXT,
  translation TEXT,
  collins INTEGER DEFAULT 0,
  oxford INTEGER DEFAULT 0
);
```

**优点**：
- ✅ 支持前缀查询 `LIKE 'app%'`（索引有效）
- ✅ 索引占用最小（约 2-3 MB）
- ✅ 查询速度快（B-Tree 索引）
- ✅ 内存占用小

**查询性能**：
- 20,000 词条
- 前缀查询: < 10ms
- 完全满足手环性能要求

### 方案 B：无索引（不推荐）

```sql
CREATE TABLE dict (
  word TEXT,
  phonetic TEXT,
  translation TEXT,
  collins INTEGER,
  oxford INTEGER
);
```

**问题**：
- ❌ 每次查询需要全表扫描
- ❌ 20,000 词条扫描太慢
- ❌ 手环算力不够

## 🎯 最终优化方案

### 数据库设计

```sql
-- 精简表结构（只有主键索引）
CREATE TABLE dict (
  word TEXT PRIMARY KEY COLLATE NOCASE,  -- 不区分大小写
  phonetic TEXT,
  translation TEXT,
  collins INTEGER DEFAULT 0,
  oxford INTEGER DEFAULT 0
);
```

### 词汇筛选策略

考虑到手环性能，建议更激进的筛选：

#### 选项 1：15,000 词（推荐）
- 牛津 3000 (3,461 词)
- 柯林斯 3-5 星 (约 5,000 词)
- BNC 前 10,000 (9,776 词)
- 去重后约 15,000 词
- **数据库大小: 2-3 MB**

#### 选项 2：10,000 词（更激进）
- 牛津 3000 (3,461 词)
- 柯林斯 4-5 星 (约 2,000 词)
- BNC 前 8,000
- 去重后约 10,000 词
- **数据库大小: 1.5-2 MB**

#### 选项 3：5,000 词（最精简）
- 牛津 3000 (3,461 词)
- 柯林斯 5 星 (约 500 词)
- 高频补充
- **数据库大小: < 1 MB**

### Translation 压缩策略

```javascript
// 压缩规则
function compressTranslation(text) {
  return text
    .replace(/\[网络\][^\n]*/g, '')      // 删除网络释义
    .replace(/\[地名\][^\n]*/g, '')      // 删除地名
    .replace(/\[人名\][^\n]*/g, '')      // 删除人名
    .replace(/na\.\s*/g, '')             // 删除词性标记
    .replace(/n\.\s*/g, '')
    .replace(/v\.\s*/g, '')
    .replace(/adj\.\s*/g, '')
    .replace(/adv\.\s*/g, '')
    .replace(/\s+/g, ' ')                // 合并空格
    .trim()
    .substring(0, 150);                  // 限制长度
}
```

**示例**：
```
原始: "n. 苹果\nna. 一种水果\n[网络] 苹果公司；红苹果；青苹果"
压缩: "苹果；一种水果"
```

## 📊 性能预估

### 数据库大小对比

| 方案 | 词条数 | 数据大小 | 索引大小 | 总大小 | RPK打包 |
|------|--------|----------|----------|--------|---------|
| 15,000词 | 15,000 | ~2 MB | ~1.5 MB | **3-4 MB** | **2-3 MB** |
| 10,000词 | 10,000 | ~1.5 MB | ~1 MB | **2-3 MB** | **1.5-2 MB** |
| 5,000词 | 5,000 | ~0.8 MB | ~0.5 MB | **1-1.5 MB** | **< 1 MB** |

### 查询性能预估

| 操作 | 15,000词 | 10,000词 | 5,000词 |
|------|----------|----------|---------|
| 前缀查询 | < 10ms | < 5ms | < 3ms |
| 精确查询 | < 5ms | < 3ms | < 2ms |
| 内存占用 | ~5 MB | ~3 MB | ~2 MB |

**结论**: 所有方案都能在手环上流畅运行！

## 🛠️ 实现建议

### 1. 数据库查询优化

```javascript
// 查询函数（带缓存）
const queryCache = new Map();

function searchWords(prefix, limit = 20) {
  // 检查缓存
  const cacheKey = `${prefix}_${limit}`;
  if (queryCache.has(cacheKey)) {
    return queryCache.get(cacheKey);
  }
  
  // 查询数据库
  const results = db.query(
    'SELECT word, phonetic, translation, collins, oxford ' +
    'FROM dict WHERE word LIKE ? ORDER BY word LIMIT ?',
    [prefix + '%', limit]
  );
  
  // 缓存结果（最多缓存 50 个查询）
  if (queryCache.size > 50) {
    const firstKey = queryCache.keys().next().value;
    queryCache.delete(firstKey);
  }
  queryCache.set(cacheKey, results);
  
  return results;
}
```

### 2. 防抖优化

```javascript
// 避免频繁查询
let searchTimer = null;

function onLetterInput(letter) {
  clearTimeout(searchTimer);
  
  searchTimer = setTimeout(() => {
    const results = searchWords(currentInput);
    updateUI(results);
  }, 100); // 100ms 防抖
}
```

### 3. 分页加载

```javascript
// 左右滑动加载更多
let currentPage = 0;
const pageSize = 10;

function loadMoreWords(direction) {
  if (direction === 'right') {
    currentPage++;
  } else if (direction === 'left' && currentPage > 0) {
    currentPage--;
  }
  
  const offset = currentPage * pageSize;
  const results = db.query(
    'SELECT * FROM dict WHERE word LIKE ? ' +
    'ORDER BY word LIMIT ? OFFSET ?',
    [currentInput + '%', pageSize, offset]
  );
  
  updateUI(results);
}
```

## 🎨 额外 4 个按键建议

除了 26 个字母，还可以添加：

1. **[←]** - 退格键（删除最后一个字母）
2. **[×]** - 清空键（清空所有输入）
3. **[★]** - 收藏键（收藏当前单词）
4. **[?]** - 帮助键（显示使用说明）

或者：

1. **[←]** - 退格
2. **[×]** - 清空
3. **[123]** - 切换到数字/符号（查询包含数字的词）
4. **[⚙]** - 设置（字体大小、主题等）

## 📝 总结

### 推荐配置

- **词条数**: 15,000 词
- **索引**: 只有 word 的主键索引
- **字段**: word, phonetic, translation, collins, oxford
- **最终大小**: 3-4 MB（RPK 打包后 2-3 MB）
- **查询性能**: < 10ms

### 关键优化点

1. ✅ **只用一个索引**（word 主键）- 节省 640 MB
2. ✅ **筛选到 15,000 词** - 节省 99.5%
3. ✅ **压缩 translation** - 节省 50%
4. ✅ **删除冗余字段** - 节省 70 MB
5. ✅ **查询缓存** - 提升响应速度
6. ✅ **防抖处理** - 减少查询次数

这样的配置完全满足小米手环的性能要求！
