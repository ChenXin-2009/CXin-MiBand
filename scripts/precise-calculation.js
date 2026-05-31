const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const dbPath = path.join(__dirname, '..', 'assets', 'ecdict-sqlite-28', 'stardict.db');
const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY);

console.log('=== 精确计算 30MB 可容纳词条数 ===\n');

const TARGET_SIZE_MB = 30;
const TARGET_SIZE_BYTES = TARGET_SIZE_MB * 1024 * 1024;

console.log(`目标大小: ${TARGET_SIZE_MB} MB = ${TARGET_SIZE_BYTES.toLocaleString()} 字节\n`);

// 创建临时测试数据库来精确测量
const tempDbPath = path.join(__dirname, '..', 'temp', 'test.db');

// 确保temp目录存在
if (!fs.existsSync(path.join(__dirname, '..', 'temp'))) {
  fs.mkdirSync(path.join(__dirname, '..', 'temp'));
}

// 测试不同词条数的实际大小
const testSizes = [1000, 5000, 10000, 20000, 30000, 50000];
let currentTest = 0;

console.log('正在创建测试数据库，精确测量实际大小...\n');

function testNextSize() {
  if (currentTest >= testSizes.length) {
    analyzeResults();
    return;
  }
  
  const testSize = testSizes[currentTest];
  console.log(`测试 ${testSize.toLocaleString()} 词条...`);
  
  // 删除旧的测试数据库
  if (fs.existsSync(tempDbPath)) {
    fs.unlinkSync(tempDbPath);
  }
  
  // 创建新的测试数据库
  const testDb = new sqlite3.Database(tempDbPath);
  
  testDb.serialize(() => {
    // 创建表结构（只有主键索引）
    testDb.run(`
      CREATE TABLE dict (
        word TEXT PRIMARY KEY COLLATE NOCASE,
        phonetic TEXT,
        translation TEXT,
        collins INTEGER DEFAULT 0,
        oxford INTEGER DEFAULT 0
      )
    `);
    
    // 插入数据
    const stmt = testDb.prepare(`
      INSERT INTO dict (word, phonetic, translation, collins, oxford)
      VALUES (?, ?, ?, ?, ?)
    `);
    
    db.all(`
      SELECT word, phonetic, translation, collins, oxford
      FROM stardict
      WHERE oxford > 0 OR collins > 0 OR (bnc > 0 AND bnc <= 50000)
      LIMIT ${testSize}
    `, (err, rows) => {
      if (err) {
        console.error('查询错误:', err);
        return;
      }
      
      rows.forEach(row => {
        // 压缩 translation（中度压缩）
        let translation = row.translation || '';
        translation = translation
          .replace(/\[网络\][^\n]*/g, '')
          .replace(/\[地名\][^\n]*/g, '')
          .replace(/\[人名\][^\n]*/g, '')
          .replace(/\s+/g, ' ')
          .trim()
          .substring(0, 150);
        
        stmt.run(
          row.word,
          row.phonetic,
          translation,
          row.collins || 0,
          row.oxford || 0
        );
      });
      
      stmt.finalize(() => {
        // VACUUM 压缩数据库
        testDb.run('VACUUM', (err) => {
          if (err) {
            console.error('VACUUM错误:', err);
            return;
          }
          
          testDb.close(() => {
            // 测量文件大小
            const stats = fs.statSync(tempDbPath);
            const sizeMB = (stats.size / 1024 / 1024).toFixed(2);
            const bytesPerWord = (stats.size / testSize).toFixed(2);
            const percentage = ((stats.size / TARGET_SIZE_BYTES) * 100).toFixed(1);
            
            console.log(`  实际大小: ${sizeMB} MB (${stats.size.toLocaleString()} 字节)`);
            console.log(`  每词占用: ${bytesPerWord} 字节`);
            console.log(`  占用率: ${percentage}%\n`);
            
            results.push({
              words: testSize,
              bytes: stats.size,
              sizeMB: parseFloat(sizeMB),
              bytesPerWord: parseFloat(bytesPerWord),
              percentage: parseFloat(percentage)
            });
            
            currentTest++;
            testNextSize();
          });
        });
      });
    });
  });
}

const results = [];
testNextSize();

function analyzeResults() {
  console.log('=== 实际测试结果 ===\n');
  console.log('词条数'.padEnd(12) + 
              '数据库大小'.padStart(15) + 
              '每词占用'.padStart(12) + 
              '占用率'.padStart(10));
  console.log('-'.repeat(50));
  
  results.forEach(r => {
    console.log(
      r.words.toLocaleString().padEnd(12) +
      (r.sizeMB + ' MB').padStart(15) +
      (r.bytesPerWord + ' B').padStart(12) +
      (r.percentage + '%').padStart(10)
    );
  });
  
  console.log('-'.repeat(50));
  console.log(`目标限制: ${TARGET_SIZE_MB} MB\n`);
  
  // 线性回归计算最大词条数
  if (results.length >= 2) {
    // 使用最后两个数据点计算平均每词占用
    const lastResult = results[results.length - 1];
    const avgBytesPerWord = lastResult.bytesPerWord;
    
    console.log('=== 容量计算 ===\n');
    console.log(`基于 ${lastResult.words.toLocaleString()} 词的测试：`);
    console.log(`平均每词占用: ${avgBytesPerWord} 字节\n`);
    
    // 计算不同压缩程度
    const compressionLevels = [
      { name: '当前压缩(150字符)', factor: 1.0 },
      { name: '轻度压缩(200字符)', factor: 1.15 },
      { name: '重度压缩(100字符)', factor: 0.85 },
      { name: '极限压缩(50字符)', factor: 0.70 },
    ];
    
    console.log('不同压缩策略下的最大词条数：\n');
    console.log('压缩策略'.padEnd(25) + '每词占用'.padStart(12) + '最大词条数'.padStart(15) + '实际大小'.padStart(12));
    console.log('-'.repeat(65));
    
    compressionLevels.forEach(level => {
      const bytesPerWord = avgBytesPerWord * level.factor;
      const maxWords = Math.floor(TARGET_SIZE_BYTES / bytesPerWord);
      const actualSizeMB = (maxWords * bytesPerWord / 1024 / 1024).toFixed(2);
      
      console.log(
        level.name.padEnd(25) +
        (bytesPerWord.toFixed(1) + ' B').padStart(12) +
        maxWords.toLocaleString().padStart(15) +
        (actualSizeMB + ' MB').padStart(12)
      );
    });
    
    console.log('\n');
  }
  
  // 分析成分占比
  analyzeComponents();
}

function analyzeComponents() {
  console.log('=== 数据库成分分析 ===\n');
  
  // 使用 50000 词的测试数据库
  const result50k = results.find(r => r.words === 50000);
  
  if (!result50k) {
    console.log('没有 50000 词的测试数据\n');
    compareWithOthers();
    return;
  }
  
  console.log(`基于 50,000 词的数据库 (${result50k.sizeMB} MB)：\n`);
  
  // 重新打开测试数据库分析
  const testDb = new sqlite3.Database(tempDbPath, sqlite3.OPEN_READONLY);
  
  testDb.get(`
    SELECT 
      SUM(LENGTH(word)) as word_bytes,
      SUM(LENGTH(phonetic)) as phonetic_bytes,
      SUM(LENGTH(translation)) as translation_bytes,
      COUNT(*) * 8 as int_bytes,
      COUNT(*) as count
    FROM dict
  `, (err, row) => {
    if (err) {
      console.error('分析错误:', err);
      testDb.close();
      compareWithOthers();
      return;
    }
    
    const wordBytes = row.word_bytes || 0;
    const phoneticBytes = row.phonetic_bytes || 0;
    const translationBytes = row.translation_bytes || 0;
    const intBytes = row.int_bytes || 0;
    const totalDataBytes = wordBytes + phoneticBytes + translationBytes + intBytes;
    const totalDbBytes = result50k.bytes;
    const indexBytes = totalDbBytes - totalDataBytes;
    
    console.log('字段名'.padEnd(20) + '大小(MB)'.padStart(12) + '占比'.padStart(10));
    console.log('-'.repeat(43));
    
    const components = [
      { name: 'word 字段', bytes: wordBytes },
      { name: 'phonetic 字段', bytes: phoneticBytes },
      { name: 'translation 字段', bytes: translationBytes },
      { name: 'collins+oxford', bytes: intBytes },
      { name: '小计(字段数据)', bytes: totalDataBytes },
      { name: '索引+元数据', bytes: indexBytes },
      { name: '总计', bytes: totalDbBytes },
    ];
    
    components.forEach(comp => {
      const mb = (comp.bytes / 1024 / 1024).toFixed(2);
      const percentage = ((comp.bytes / totalDbBytes) * 100).toFixed(1);
      const name = comp.name === '小计(字段数据)' || comp.name === '总计' ? 
                   `\n${comp.name}` : comp.name;
      
      console.log(
        name.padEnd(20) +
        (mb + ' MB').padStart(12) +
        (percentage + '%').padStart(10)
      );
    });
    
    console.log('\n关键发现：');
    console.log(`- 字段数据占 ${((totalDataBytes / totalDbBytes) * 100).toFixed(1)}%`);
    console.log(`- 索引+元数据占 ${((indexBytes / totalDbBytes) * 100).toFixed(1)}%`);
    console.log(`- Translation 占字段数据的 ${((translationBytes / totalDataBytes) * 100).toFixed(1)}%\n`);
    
    testDb.close();
    compareWithOthers();
  });
}

function compareWithOthers() {
  console.log('=== 与其他词典对比 ===\n');
  
  console.log('其他人的词典: 4 MB = 50,000 词');
  console.log('计算: 4 MB / 50,000 = 81.92 字节/词\n');
  
  const result50k = results.find(r => r.words === 50000);
  if (result50k) {
    console.log(`你的数据库: ${result50k.sizeMB} MB = 50,000 词`);
    console.log(`计算: ${result50k.sizeMB} MB / 50,000 = ${result50k.bytesPerWord} 字节/词\n`);
    
    if (result50k.bytesPerWord > 82) {
      console.log('⚠️  你的数据库每词占用更多空间，可能原因：');
      console.log('1. Translation 字段更长（更详细的翻译）');
      console.log('2. 包含 phonetic 字段（其他词典可能没有）');
      console.log('3. 包含 collins 和 oxford 标记');
      console.log('4. 索引开销（SQLite 的 B-Tree 索引）\n');
      
      console.log('优化建议：');
      console.log('1. 进一步压缩 translation（限制到 100 字符）');
      console.log('2. 考虑删除 phonetic 字段（如果不需要音标）');
      console.log('3. 使用更激进的压缩算法\n');
    }
  }
  
  // 计算 30MB 可以放多少词
  console.log('=== 30MB 容量计算 ===\n');
  
  if (result50k) {
    const bytesPerWord = result50k.bytesPerWord;
    const maxWords = Math.floor(TARGET_SIZE_BYTES / bytesPerWord);
    
    console.log(`基于实测数据 (${bytesPerWord} 字节/词)：`);
    console.log(`30 MB 可容纳: ${maxWords.toLocaleString()} 词\n`);
    
    // 如果按其他人的标准
    const othersMaxWords = Math.floor(TARGET_SIZE_BYTES / 81.92);
    console.log(`如果优化到其他词典水平 (81.92 字节/词)：`);
    console.log(`30 MB 可容纳: ${othersMaxWords.toLocaleString()} 词\n`);
  }
  
  db.close();
  
  // 清理测试文件
  if (fs.existsSync(tempDbPath)) {
    fs.unlinkSync(tempDbPath);
  }
  
  console.log('测试完成！');
}
