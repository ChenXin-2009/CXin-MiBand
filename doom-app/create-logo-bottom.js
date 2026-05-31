const fs = require('fs');
const path = require('path');

// 创建一个256x256的PNG底部logo，毁灭战士风格
function createLogoBottom() {
  const width = 256;
  const height = 256;
  
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
  
  // 创建图像数据 - 深红色圆形背景，准星和装饰图案
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
        // 深红色背景 RGB(164, 42, 36)
        pixelData[pixelStart] = 164;     // R
        pixelData[pixelStart + 1] = 42;  // G
        pixelData[pixelStart + 2] = 36;  // B
        pixelData[pixelStart + 3] = 255; // A (不透明)
        
        // 绘制准星图案（十字）
        const crosshairSize = 50;
        const crosshairThickness = 8;
        const crosshairGap = 10;
        
        // 水平线（左右两段）
        const isHorizontalLeft = Math.abs(y - centerY) < crosshairThickness && 
                                 x >= centerX - crosshairSize && 
                                 x <= centerX - crosshairGap;
        const isHorizontalRight = Math.abs(y - centerY) < crosshairThickness && 
                                  x >= centerX + crosshairGap && 
                                  x <= centerX + crosshairSize;
        
        // 垂直线（上下两段）
        const isVerticalTop = Math.abs(x - centerX) < crosshairThickness && 
                              y >= centerY - crosshairSize && 
                              y <= centerY - crosshairGap;
        const isVerticalBottom = Math.abs(x - centerX) < crosshairThickness && 
                                 y >= centerY + crosshairGap && 
                                 y <= centerY + crosshairSize;
        
        // 中心点
        const isCenterDot = distance < 5;
        
        // 外圈装饰（四个角的小方块）
        const cornerSize = 12;
        const cornerDistance = 70;
        const isCornerTL = x >= centerX - cornerDistance - cornerSize && 
                          x <= centerX - cornerDistance &&
                          y >= centerY - cornerDistance - cornerSize && 
                          y <= centerY - cornerDistance;
        const isCornerTR = x >= centerX + cornerDistance && 
                          x <= centerX + cornerDistance + cornerSize &&
                          y >= centerY - cornerDistance - cornerSize && 
                          y <= centerY - cornerDistance;
        const isCornerBL = x >= centerX - cornerDistance - cornerSize && 
                          x <= centerX - cornerDistance &&
                          y >= centerY + cornerDistance && 
                          y <= centerY + cornerDistance + cornerSize;
        const isCornerBR = x >= centerX + cornerDistance && 
                          x <= centerX + cornerDistance + cornerSize &&
                          y >= centerY + cornerDistance && 
                          y <= centerY + cornerDistance + cornerSize;
        
        if (isHorizontalLeft || isHorizontalRight || isVerticalTop || isVerticalBottom || 
            isCenterDot || isCornerTL || isCornerTR || isCornerBL || isCornerBR) {
          // 白色准星和装饰
          pixelData[pixelStart] = 255;     // R
          pixelData[pixelStart + 1] = 255; // G
          pixelData[pixelStart + 2] = 255; // B
          pixelData[pixelStart + 3] = 255; // A
        }
        
        // 添加像素化的边框装饰
        const pixelSize = 10;
        const isPixelBorder = (Math.floor(x / pixelSize) + Math.floor(y / pixelSize)) % 2 === 0 &&
                              distance > radius - 20 && distance < radius - 8;
        
        if (isPixelBorder) {
          // 稍微深一点的红色作为边框装饰
          pixelData[pixelStart] = 140;     // R
          pixelData[pixelStart + 1] = 30;  // G
          pixelData[pixelStart + 2] = 25;  // B
          pixelData[pixelStart + 3] = 255; // A
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

// 保存底部logo
const logoPath = path.join(__dirname, 'src', 'common', 'logo-bottom.png');
const logoData = createLogoBottom();
fs.writeFileSync(logoPath, logoData);

console.log('✅ 毁灭应用底部Logo已创建：', logoPath);
console.log('📐 尺寸：256x256 像素');
console.log('🎨 样式：深红色圆形背景，白色准星和装饰图案');
console.log('💡 提示：Logo用于页面底部显示，带有半透明效果');
