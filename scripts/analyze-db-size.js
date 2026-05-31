const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const dbPath = path.join(__dirname, '..', 'assets', 'ecdict-sqlite-28', 'stardict.db');
const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY);

console.log('=== 数据库字段体积分析 ===\n');

const totalSize = fs.statSync(dbPath).size;
console.log(`数据库总大小: ${(totalSize / 1024 / 1024).toFixed(2)} MB (${totalSize.toLocaleString()} 字节)\n`);

// 分析每个字段的平均长度和总占用
const fields = [
  'word', 'sw', 'phonetic', 'definition', 'translation', 
  'pos', 'collins', 'oxford', 'tag', 'bnc', 'frq', 'exchange', 'detail', 'audio'
];

let completed = 0;
const fieldSizes = {};

console.log('正在分析各字段占用空间...\n');

fields.forEach(field => {
  // 计算字段的总字节数和平均长度
  db.get(`
    SELECT 
      SUM(LENGTH(${field})) as total_bytes,
      AVG(LENGTH(${field})) as avg_length,
      MAX(LENGTH(${field})) as max_length,
      COUNT(CASE WHEN ${field} IS NOT NULL AND ${field} != '' THEN 1 END) as non_null_count,
      COUNT(*) as total_count
    FROM stardict
  `, (err, row) => {
    if (err) {
      console.error(`分析 ${field} 错误:`, err);
      completed++;
      return;
    }
    
    const totalBytes = row.total_bytes || 0;
    const avgLength = row.avg_length || 0;
    const maxLength = row.max_length || 0;
    const nonNullCount = row.non_null_count || 0;
    const totalCount = row.total_count || 0;
    const percentage = ((totalBytes / totalSize) * 100).toFixed(2);
    
    fieldSizes[field] = {
      totalBytes,
      totalMB: (totalBytes / 1024 / 1024).toFixed(2),
      avgLength: avgLength.toFixed(2),
      maxLength,
      nonNullCount,
      totalCount,
      percentage,
      fillRate: ((nonNullCount / totalCount) * 100).toFixed(2)
    };
    
    completed++;
    
    if (completed === fields.length) {
      displayResults();
    }
  });
});

function displayResults() {
  console.log('=== 字段体积占用排行 ===\n');
  
  // 按体积排序
  const sortedFields = Object.entries(fieldSizes)
    .sort((a, b) => b[1].totalBytes - a[1].totalBytes);
  
  console.log('字段名'.padEnd(15) + 
              '总大小(MB)'.padStart(12) + 
              '占比'.padStart(10) + 
              '平均长度'.padStart(12) + 
              '最大长度'.padStart(12) + 
              '填充率'.padStart(10));
  console.log('-'.repeat(80));
  
  let totalFieldBytes = 0;
  sortedFields.forEach(([field, stats]) => {
    totalFieldBytes += stats.totalBytes;
    console.log(
      field.padEnd(15) + 
      stats.totalMB.padStart(12) + 
      (stats.percentage + '%').padStart(10) + 
      stats.avgLength.padStart(12) + 
      stats.maxLength.toString().padStart(12) + 
      (stats.fillRate + '%').padStart(10)
    );
  });
  
  console.log('-'.repeat(80));
  console.log(`字段数据总计: ${(totalFieldBytes / 1024 / 1024).toFixed(2)} MB (${((totalFieldBytes / totalSize) * 100).toFixed(2)}%)`);
  console.log(`索引+元数据: ${((totalSize - totalFieldBytes) / 1024 / 1024).toFixed(2)} MB (${(((totalSize - totalFieldBytes) / totalSize) * 100).toFixed(2)}%)\n`);
  
  // 分析最占空间的字段
  analyzeTopFields(sortedFields);
}

function analyzeTopFields(sortedFields) {
  console.log('=== 体积优化建议 ===\n');
  
  const top5 = sortedFields.slice(0, 5);
  let cumulativeSize = 0;
  let cumulativePercentage = 0;
  
  console.log('前5大字段占用分析：\n');
  
  top5.forEach(([field, stats], index) => {
    cumulativeSize += parseFloat(stats.totalMB);
    cumulativePercentage += parseFloat(stats.percentage);
    
    console.log(`${index + 1}. ${field} - ${stats.totalMB} MB (${stats.percentage}%)`);
    console.log(`   平均长度: ${stats.avgLength} 字符, 最大: ${stats.maxLength} 字符`);
    console.log(`   填充率: ${stats.fillRate}%`);
    
    // 给出具体建议
    if (field === 'translation') {
      console.log(`   💡 建议: 这是最大的字段，可以：`);
      console.log(`      - 删除 [网络] 等标记和内容`);
      console.log(`      - 限制翻译长度（如最多200字符）`);
      console.log(`      - 删除重复和冗余的释义`);
      console.log(`      - 预计可减少 40-60% 体积`);
    } else if (field === 'definition') {
      console.log(`   💡 建议: 英文释义，手表上可能用处不大`);
      console.log(`      - 可以完全删除此字段`);
      console.log(`      - 节省约 ${stats.totalMB} MB`);
    } else if (field === 'detail') {
      console.log(`   💡 建议: 详细信息字段`);
      console.log(`      - 填充率极低，可以删除`);
      console.log(`      - 节省约 ${stats.totalMB} MB`);
    } else if (field === 'exchange') {
      console.log(`   💡 建议: 词形变化`);
      console.log(`      - 手表查词可能不需要`);
      console.log(`      - 可以删除节省 ${stats.totalMB} MB`);
    } else if (field === 'word' || field === 'sw') {
      console.log(`   💡 建议: 核心字段，必须保留`);
    } else {
      console.log(`   💡 建议: 根据需求决定是否保留`);
    }
    console.log('');
  });
  
  console.log(`前5大字段累计: ${cumulativeSize.toFixed(2)} MB (${cumulativePercentage.toFixed(2)}%)\n`);
  
  // 采样分析translation字段的内容
  analyzeTranslationContent();
}

function analyzeTranslationContent() {
  console.log('=== Translation 字段内容分析 ===\n');
  
  // 随机采样100条记录
  db.all(`
    SELECT word, translation, LENGTH(translation) as len
    FROM stardict 
    WHERE translation IS NOT NULL 
    ORDER BY RANDOM() 
    LIMIT 10
  `, (err, rows) => {
    if (err) {
      console.error('采样错误:', err);
      db.close();
      return;
    }
    
    console.log('随机采样10条记录：\n');
    rows.forEach((row, i) => {
      console.log(`${i + 1}. ${row.word} (${row.len}字符)`);
      console.log(`   ${row.translation.substring(0, 150)}${row.len > 150 ? '...' : ''}`);
      console.log('');
    });
    
    // 分析包含特定标记的记录数
    analyzeTranslationPatterns();
  });
}

function analyzeTranslationPatterns() {
  console.log('=== Translation 内容模式分析 ===\n');
  
  const patterns = [
    { name: '包含[网络]', pattern: '%[网络]%' },
    { name: '包含[地名]', pattern: '%[地名]%' },
    { name: '包含[人名]', pattern: '%[人名]%' },
    { name: '包含na.', pattern: '%na.%' },
    { name: '包含n.', pattern: '%n.%' },
    { name: '包含v.', pattern: '%v.%' },
    { name: '包含adj.', pattern: '%adj.%' },
    { name: '长度>500', sql: 'LENGTH(translation) > 500' },
    { name: '长度>1000', sql: 'LENGTH(translation) > 1000' },
    { name: '长度>2000', sql: 'LENGTH(translation) > 2000' },
  ];
  
  let completed = 0;
  const results = [];
  
  patterns.forEach(p => {
    const sql = p.sql || `translation LIKE '${p.pattern}'`;
    db.get(`SELECT COUNT(*) as count FROM stardict WHERE ${sql}`, (err, row) => {
      if (err) {
        console.error(`分析 ${p.name} 错误:`, err);
        return;
      }
      
      results.push({ name: p.name, count: row.count });
      completed++;
      
      if (completed === patterns.length) {
        results.forEach(r => {
          const percentage = ((r.count / 3402564) * 100).toFixed(2);
          console.log(`${r.name.padEnd(20)}: ${r.count.toLocaleString().padStart(10)} (${percentage}%)`);
        });
        
        console.log('\n');
        provideOptimizationPlan();
      }
    });
  });
}

function provideOptimizationPlan() {
  console.log('=== 优化方案（基于体积分析）===\n');
  
  console.log('【方案A：字段删除】');
  console.log('删除以下字段可节省大量空间：');
  
  const fieldsToDelete = ['definition', 'detail', 'exchange', 'audio', 'tag', 'pos'];
  let savedSpace = 0;
  
  fieldsToDelete.forEach(field => {
    if (fieldSizes[field]) {
      savedSpace += parseFloat(fieldSizes[field].totalMB);
      console.log(`  - ${field.padEnd(15)}: 节省 ${fieldSizes[field].totalMB} MB`);
    }
  });
  console.log(`  总计节省: ${savedSpace.toFixed(2)} MB\n`);
  
  console.log('【方案B：Translation 压缩】');
  console.log('Translation 字段优化策略：');
  console.log('  1. 删除 [网络]、[地名]、[人名] 等标记及其内容');
  console.log('  2. 删除词性标记（na., n., v., adj.等）');
  console.log('  3. 限制每个词条翻译最大长度为 200 字符');
  console.log('  4. 删除重复的释义');
  if (fieldSizes['translation']) {
    const translationSize = parseFloat(fieldSizes['translation'].totalMB);
    console.log(`  预计可从 ${translationSize} MB 压缩到 ${(translationSize * 0.3).toFixed(2)}-${(translationSize * 0.5).toFixed(2)} MB`);
    console.log(`  节省: ${(translationSize * 0.5).toFixed(2)}-${(translationSize * 0.7).toFixed(2)} MB\n`);
  }
  
  console.log('【方案C：词条筛选】');
  console.log('只保留常用词汇（20,000词）：');
  console.log(`  从 3,402,564 词减少到 20,000 词`);
  console.log(`  体积减少约 99.4%`);
  console.log(`  预计: ${(totalSize / 1024 / 1024 * 0.006).toFixed(2)} MB\n`);
  
  console.log('【综合优化预估】');
  console.log('方案A + 方案B + 方案C：');
  console.log('  1. 保留 20,000 核心词汇');
  console.log('  2. 只保留字段: word, phonetic, translation(压缩), collins, oxford');
  console.log('  3. 压缩 translation 内容');
  console.log('  4. VACUUM 压缩数据库');
  console.log(`  预计最终大小: 3-8 MB`);
  console.log(`  RPK 打包后: 2-5 MB (有额外压缩)\n`);
  
  db.close();
}
