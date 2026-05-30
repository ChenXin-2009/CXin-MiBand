const fs = require('fs');
const path = require('path');

// 创建一个192x192的PNG图标，手电筒样式
function createIcon() {
  const width = 192;
  const height = 192;
  
  // PNG文件头
  const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  
  // IHDR chunk (图像头) - 使用RGBA格式以支持透明度
  const ihdr = Buffer.alloc(25);
  ihdr.writeUInt32BE(13, 0); // chunk长度
  ihdr.write('IHDR', 4);
  ihdr.writeUInt32BE(width, 8);
  ihdr.writeUInt32BE(height, 12);
  ihdr.writeUInt8(8, 16); // 位深度
  ihdr.writeUInt8(6, 17); // 颜色类型 (6 = RGBA)
  ihdr.writeUInt8(0, 18); // 压缩方法
  ihdr.writeUInt8(0, 19); // 过滤方法
  ihdr.writeUInt8(0, 20); // 隔行扫描
  
  // 计算CRC
  const zlib = require('zlib');
  const crc = zlib.crc32(ihdr.slice(4, 21));
  ihdr.writeUInt32BE(crc, 21);
  
  // 创建图像数据 - 黄色圆形背景，手电筒图案
  const pixelData = Buffer.alloc(height * (1 + width * 4)); // RGBA = 4字节
  
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = width * 0.45; // 圆形半径
  
  for (let y = 0; y < height; y++) {
    const rowStart = y * (1 + width * 4);
    pixelData[rowStart] = 0; // 过滤类型
    
    for (let x = 0; x < width; x++) {
      const pixelStart = rowStart + 1 + x * 4;
      
      // 计算到中心的距离
      const dx = x - centerX;
      const dy = y - centerY;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      // 在圆形内
      if (distance < radius) {
        // 黄色背景 RGB(255, 193, 7)
        pixelData[pixelStart] = 255;     // R
        pixelData[pixelStart + 1] = 193; // G
        pixelData[pixelStart + 2] = 7;   // B
        pixelData[pixelStart + 3] = 255; // A (不透明)
        
        // 绘制手电筒图案（简化版）
        // 手电筒头部（矩形）
        const headTop = centerY - 50;
        const headBottom = centerY - 20;
        const headLeft = centerX - 30;
        const headRight = centerX + 30;
        
        // 手电筒身体（矩形）
        const bodyTop = centerY - 20;
        const bodyBottom = centerY + 40;
        const bodyLeft = centerX - 20;
        const bodyRight = centerX + 20;
        
        // 光束（三角形）
        const beamTop = centerY - 50;
        const beamHeight = 30;
        
        const isHead = y >= headTop && y <= headBottom && x >= headLeft && x <= headRight;
        const isBody = y >= bodyTop && y <= bodyBottom && x >= bodyLeft && x <= bodyRight;
        
        // 光束效果
        const isBeam = y >= beamTop - beamHeight && y <= beamTop && 
                       Math.abs(x - centerX) <= (beamTop - y) * 0.8;
        
        if (isHead || isBody) {
          // 深灰色手电筒
          pixelData[pixelStart] = 60;      // R
          pixelData[pixelStart + 1] = 60;  // G
          pixelData[pixelStart + 2] = 60;  // B
          pixelData[pixelStart + 3] = 255; // A
        } else if (isBeam) {
          // 白色光束
          pixelData[pixelStart] = 255;     // R
          pixelData[pixelStart + 1] = 255; // G
          pixelData[pixelStart + 2] = 255; // B
          pixelData[pixelStart + 3] = 200; // A (半透明)
        }
      } else {
        // 圆形外透明
        pixelData[pixelStart] = 0;
        pixelData[pixelStart + 1] = 0;
        pixelData[pixelStart + 2] = 0;
        pixelData[pixelStart + 3] = 0; // 完全透明
      }
    }
  }
  
  // 压缩图像数据
  const compressed = zlib.deflateSync(pixelData);
  
  // IDAT chunk (图像数据)
  const idat = Buffer.alloc(12 + compressed.length);
  idat.writeUInt32BE(compressed.length, 0);
  idat.write('IDAT', 4);
  compressed.copy(idat, 8);
  const idatCrc = zlib.crc32(idat.slice(4, 8 + compressed.length));
  idat.writeUInt32BE(idatCrc, 8 + compressed.length);
  
  // IEND chunk (结束标记)
  const iend = Buffer.from([0, 0, 0, 0, 73, 69, 78, 68, 174, 66, 96, 130]);
  
  // 组合所有部分
  const png = Buffer.concat([signature, ihdr, idat, iend]);
  
  return png;
}

// 保存图标
const iconPath = path.join(__dirname, 'src', 'common', 'logo.png');
const iconData = createIcon();
fs.writeFileSync(iconPath, iconData);

console.log('✅ 手电筒应用图标已创建：', iconPath);
console.log('📐 尺寸：192x192 像素');
console.log('🎨 样式：黄色圆形背景，手电筒图案');
console.log('💡 提示：图标为标准尺寸，应该能在手环上正常显示');
