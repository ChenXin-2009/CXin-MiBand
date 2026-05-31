const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const dbPath = path.join(__dirname, '..', 'assets', 'ecdict-sqlite-28', 'stardict.db');
const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY);

console.log('=== ECDICT 数据库详细分析 ===\n');
console.log(`数据库路径: ${dbPath}`);
console.log(`数据库大小: ${(fs.statSync(dbPath).size / 1024 / 1024).toFixed(2)} MB\n`);

const analysis = {};

// 分析各字段的使用情况
db.get(`SELECT COUNT(*) as total FROM stardict`, (err, row) => {
  if (err) {
    console.error('错误:', err);
    db.close();
    return;
  }
  
  const total = row.total;
  analysis.total = total;
  console.log(`总词条数: ${total.toLocaleString()}\n`);
  
  // 分析各字段的非空率
  const fields = [
    'word', 'sw', 'phonetic', 'definition', 'translation', 
    'pos', 'collins', 'oxford', 'tag', 'bnc', 'frq', 'exchange', 'detail', 'audio'
  ];
  
  let completed = 0;
  const fieldStats = {};
  
  fields.forEach(field => {
    db.get(`SELECT COUNT(*) as count FROM stardict WHERE ${field} IS NOT NULL AND ${field} != ''`, (err, row) => {
      if (err) {
        console.error(`分析 ${field} 错误:`, err);
        return;
      }
      
      const count = row.count;
      const percentage = ((count / total) * 100).toFixed(2);
      fieldStats[field] = { count, percentage };
      
      completed++;
      if (completed === fields.length) {
        // 所有字段分析完成
        console.log('=== 字段使用率分析 ===');
        Object.keys(fieldStats).forEach(field => {
          const stat = fieldStats[field];
          console.log(`${field.padEnd(15)}: ${stat.count.toLocaleString().padStart(12)} (${stat.percentage}%)`);
        });
        
        // 分析常用词汇
        analyzeFrequency();
      }
    });
  });
});

function analyzeFrequency() {
  console.log('\n=== 词频分析 ===');
  
  // 分析有词频数据的词条
  db.get(`SELECT COUNT(*) as count FROM stardict WHERE frq IS NOT NULL AND frq > 0`, (err, row) => {
    if (err) {
      console.error('词频分析错误:', err);
      return;
    }
    console.log(`有词频数据的词条: ${row.count.toLocaleString()}`);
  });
  
  // 分析BNC词频
  db.get(`SELECT COUNT(*) as count FROM stardict WHERE bnc IS NOT NULL AND bnc > 0`, (err, row) => {
    if (err) {
      console.error('BNC分析错误:', err);
      return;
    }
    console.log(`有BNC词频的词条: ${row.count.toLocaleString()}`);
  });
  
  // 分析柯林斯星级
  db.get(`SELECT COUNT(*) as count FROM stardict WHERE collins IS NOT NULL AND collins > 0`, (err, row) => {
    if (err) {
      console.error('柯林斯分析错误:', err);
      return;
    }
    console.log(`有柯林斯星级的词条: ${row.count.toLocaleString()}`);
  });
  
  // 分析牛津3000
  db.get(`SELECT COUNT(*) as count FROM stardict WHERE oxford IS NOT NULL AND oxford > 0`, (err, row) => {
    if (err) {
      console.error('牛津分析错误:', err);
      return;
    }
    console.log(`牛津3000词汇: ${row.count.toLocaleString()}`);
  });
  
  // 分析词长分布
  setTimeout(() => {
    analyzeWordLength();
  }, 1000);
}

function analyzeWordLength() {
  console.log('\n=== 词长分布 ===');
  
  db.all(`
    SELECT 
      CASE 
        WHEN LENGTH(word) <= 5 THEN '1-5字符'
        WHEN LENGTH(word) <= 10 THEN '6-10字符'
        WHEN LENGTH(word) <= 15 THEN '11-15字符'
        WHEN LENGTH(word) <= 20 THEN '16-20字符'
        ELSE '20+字符'
      END as length_range,
      COUNT(*) as count
    FROM stardict
    GROUP BY length_range
    ORDER BY MIN(LENGTH(word))
  `, (err, rows) => {
    if (err) {
      console.error('词长分析错误:', err);
      return;
    }
    
    rows.forEach(row => {
      console.log(`${row.length_range.padEnd(15)}: ${row.count.toLocaleString()}`);
    });
    
    // 查看最长的词
    db.all(`SELECT word, LENGTH(word) as len FROM stardict ORDER BY len DESC LIMIT 10`, (err, rows) => {
      if (err) {
        console.error('最长词查询错误:', err);
        return;
      }
      console.log('\n最长的10个词条:');
      rows.forEach((row, i) => {
        console.log(`  ${i+1}. ${row.word} (${row.len}字符)`);
      });
      
      // 提供优化建议
      setTimeout(() => {
        provideOptimizationSuggestions();
      }, 500);
    });
  });
}

function provideOptimizationSuggestions() {
  console.log('\n=== 数据库优化建议 ===\n');
  
  console.log('1. 【按词频筛选】');
  console.log('   - 保留高频词汇（如BNC前20000词）');
  console.log('   - 保留柯林斯星级词汇');
  console.log('   - 保留牛津3000核心词汇');
  
  console.log('\n2. 【删除冗余字段】');
  console.log('   - 删除detail字段（通常很长且使用率低）');
  console.log('   - 删除audio字段（手表上可能无法播放）');
  console.log('   - 删除exchange字段（词形变化，可选）');
  console.log('   - 只保留: word, phonetic, translation, collins, oxford');
  
  console.log('\n3. 【压缩翻译内容】');
  console.log('   - 简化translation字段，删除冗余信息');
  console.log('   - 删除网络释义等额外内容');
  
  console.log('\n4. 【数据库压缩】');
  console.log('   - 使用VACUUM命令压缩数据库');
  console.log('   - 删除索引后重建');
  
  console.log('\n5. 【分级数据库】');
  console.log('   - 创建核心词库（5000-10000词）');
  console.log('   - 创建扩展词库（可选下载）');
  
  // 估算优化后的大小
  estimateOptimizedSize();
}

function estimateOptimizedSize() {
  console.log('\n=== 优化后大小估算 ===\n');
  
  // 估算保留高频词的大小
  const queries = [
    { name: '牛津3000', sql: 'SELECT COUNT(*) as count FROM stardict WHERE oxford > 0' },
    { name: '柯林斯1-5星', sql: 'SELECT COUNT(*) as count FROM stardict WHERE collins > 0' },
    { name: 'BNC前10000', sql: 'SELECT COUNT(*) as count FROM stardict WHERE bnc > 0 AND bnc <= 10000' },
    { name: 'BNC前20000', sql: 'SELECT COUNT(*) as count FROM stardict WHERE bnc > 0 AND bnc <= 20000' },
  ];
  
  let completed = 0;
  queries.forEach(query => {
    db.get(query.sql, (err, row) => {
      if (err) {
        console.error(`查询 ${query.name} 错误:`, err);
        return;
      }
      
      const count = row.count;
      const estimatedSize = (count / 3402564 * 811).toFixed(2);
      console.log(`${query.name.padEnd(20)}: ${count.toLocaleString().padStart(8)} 词条 ≈ ${estimatedSize} MB`);
      
      completed++;
      if (completed === queries.length) {
        console.log('\n注: 以上估算未考虑字段删除和内容压缩的效果');
        console.log('实际优化后可能更小（预计可减少50-70%）\n');
        
        db.close();
      }
    });
  });
}
