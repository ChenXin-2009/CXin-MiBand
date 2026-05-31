const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, 'assets', 'ecdict-sqlite-28', 'stardict.db');
const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY);

console.log('=== 数据库分析 ===\n');

// 获取所有表
db.all("SELECT name FROM sqlite_master WHERE type='table'", (err, tables) => {
  if (err) {
    console.error('错误:', err);
    return;
  }
  
  console.log('表列表:', tables.map(t => t.name).join(', '));
  console.log('');
  
  tables.forEach(table => {
    const tableName = table.name;
    
    // 获取表结构
    db.all(`PRAGMA table_info(${tableName})`, (err, columns) => {
      if (err) {
        console.error(`获取 ${tableName} 结构错误:`, err);
        return;
      }
      
      console.log(`\n表: ${tableName}`);
      console.log('列:', columns.map(c => `${c.name}(${c.type})`).join(', '));
      
      // 获取记录数
      db.get(`SELECT COUNT(*) as count FROM ${tableName}`, (err, row) => {
        if (err) {
          console.error(`获取 ${tableName} 记录数错误:`, err);
          return;
        }
        console.log(`记录数: ${row.count.toLocaleString()}`);
        
        // 获取前5条记录示例
        db.all(`SELECT * FROM ${tableName} LIMIT 5`, (err, rows) => {
          if (err) {
            console.error(`获取 ${tableName} 示例错误:`, err);
            return;
          }
          console.log('示例数据:');
          rows.forEach((row, i) => {
            console.log(`  [${i+1}]`, JSON.stringify(row).substring(0, 200));
          });
        });
      });
    });
  });
  
  // 等待所有查询完成后关闭
  setTimeout(() => {
    db.close();
  }, 5000);
});
