#!/usr/bin/env node

/**
 * 创建临时图标文件
 * 这是一个 192x192 的简单 PNG 图片（蓝色背景，白色文字"测试"）
 */

const fs = require('fs');
const path = require('path');

// 这是一个最小的 1x1 透明 PNG 的 base64 编码
// 实际使用时应该替换为真实的图标
const minimalPNG = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
  'base64'
);

const iconPath = path.join(__dirname, 'src', 'common', 'logo.png');

try {
  fs.writeFileSync(iconPath, minimalPNG);
  console.log('✅ 临时图标已创建：', iconPath);
  console.log('⚠️  这只是一个 1x1 的占位图标');
  console.log('📝 请尽快替换为真实的应用图标（建议 192x192 像素）');
} catch (error) {
  console.error('❌ 创建图标失败：', error.message);
  process.exit(1);
}
