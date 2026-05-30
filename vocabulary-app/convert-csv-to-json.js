const fs = require('fs');
const path = require('path');

// CSV文件所在目录
const csvDir = path.join(__dirname, '..', 'csv_by_unit');
// 输出JSON文件的目录
const outputDir = path.join(__dirname, 'src', 'data');

// 确保输出目录存在
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// 解析CSV文件
function parseCSV(content) {
  const lines = content.split('\n');
  const words = [];
  
  // 跳过第一行（标题行）
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i].trim();
    if (!line) continue;
    
    // 简单的CSV解析（假设没有复杂的引号情况）
    const parts = line.split(',');
    if (parts.length >= 3) {
      words.push({
        english: parts[0].trim(),
        phonetic: parts[1].trim(),
        chinese: parts.slice(2).join(',').trim()
      });
    }
  }
  
  return words;
}

// 读取所有CSV文件并转换
const files = fs.readdirSync(csvDir);
const allData = {};

files.forEach(file => {
  if (file.endsWith('.csv')) {
    const filePath = path.join(csvDir, file);
    const content = fs.readFileSync(filePath, 'utf-8');
    const words = parseCSV(content);
    
    // 使用文件名（不含扩展名）作为键
    const key = file.replace('.csv', '');
    allData[key] = words;
    
    console.log(`已转换: ${file} (${words.length} 个单词)`);
  }
});

// 将所有数据写入一个JSON文件
const outputPath = path.join(outputDir, 'words.json');
fs.writeFileSync(outputPath, JSON.stringify(allData, null, 2), 'utf-8');

console.log(`\n转换完成！数据已保存到: ${outputPath}`);
console.log(`总共转换了 ${Object.keys(allData).length} 个文件`);
