#!/usr/bin/env node

/**
 * AIoT-toolkit2.0 配置检查脚本
 * 用于验证开发环境是否正确配置
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔍 开始检查 AIoT-toolkit2.0 配置...\n');

let allPassed = true;

// 检查项目
const checks = [
  {
    name: 'Node.js 版本',
    check: () => {
      try {
        const version = execSync('node --version', { encoding: 'utf8' }).trim();
        const major = parseInt(version.slice(1).split('.')[0]);
        if (major >= 14) {
          return { passed: true, message: `✅ ${version}` };
        }
        return { passed: false, message: `❌ ${version} (需要 >= 14.0.0)` };
      } catch (error) {
        return { passed: false, message: '❌ Node.js 未安装' };
      }
    }
  },
  {
    name: 'npm 版本',
    check: () => {
      try {
        const version = execSync('npm --version', { encoding: 'utf8' }).trim();
        return { passed: true, message: `✅ ${version}` };
      } catch (error) {
        return { passed: false, message: '❌ npm 未安装' };
      }
    }
  },
  {
    name: 'aiot-toolkit 安装',
    check: () => {
      const packageJsonPath = path.join(__dirname, 'package.json');
      if (!fs.existsSync(packageJsonPath)) {
        return { passed: false, message: '❌ package.json 不存在' };
      }
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      if (packageJson.devDependencies && packageJson.devDependencies['aiot-toolkit']) {
        const version = packageJson.devDependencies['aiot-toolkit'];
        return { passed: true, message: `✅ ${version}` };
      }
      return { passed: false, message: '❌ 未安装' };
    }
  },
  {
    name: 'aiot 命令可用',
    check: () => {
      try {
        const version = execSync('npx aiot --version', { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
        return { passed: true, message: `✅ v${version}` };
      } catch (error) {
        return { passed: false, message: '❌ 命令不可用' };
      }
    }
  },
  {
    name: 'node_modules 目录',
    check: () => {
      const nodeModulesPath = path.join(__dirname, 'node_modules');
      if (fs.existsSync(nodeModulesPath)) {
        return { passed: true, message: '✅ 存在' };
      }
      return { passed: false, message: '❌ 不存在（运行 npm install）' };
    }
  },
  {
    name: '.aiotrc.js 配置文件',
    check: () => {
      const configPath = path.join(__dirname, '.aiotrc.js');
      if (fs.existsSync(configPath)) {
        return { passed: true, message: '✅ 存在' };
      }
      return { passed: false, message: '⚠️  不存在（可选）' };
    }
  },
  {
    name: 'src 目录',
    check: () => {
      const srcPath = path.join(__dirname, 'src');
      if (fs.existsSync(srcPath)) {
        return { passed: true, message: '✅ 存在' };
      }
      return { passed: false, message: '❌ 不存在' };
    }
  },
  {
    name: 'manifest.json',
    check: () => {
      const manifestPath = path.join(__dirname, 'src', 'manifest.json');
      if (fs.existsSync(manifestPath)) {
        return { passed: true, message: '✅ 存在' };
      }
      return { passed: false, message: '❌ 不存在' };
    }
  },
  {
    name: '应用图标 (logo.png)',
    check: () => {
      const logoPath = path.join(__dirname, 'src', 'common', 'logo.png');
      if (fs.existsSync(logoPath)) {
        const stats = fs.statSync(logoPath);
        return { passed: true, message: `✅ 存在 (${(stats.size / 1024).toFixed(2)} KB)` };
      }
      return { passed: false, message: '❌ 不存在（需要添加）' };
    }
  }
];

// 执行检查
checks.forEach(({ name, check }) => {
  const result = check();
  console.log(`${name.padEnd(25)} ${result.message}`);
  if (!result.passed && !result.message.includes('⚠️')) {
    allPassed = false;
  }
});

console.log('\n' + '='.repeat(60));

if (allPassed) {
  console.log('✅ 所有检查通过！环境配置正确。');
  console.log('\n下一步：');
  console.log('  1. 确保 src/common/logo.png 存在');
  console.log('  2. 运行 npm run init 初始化模拟器');
  console.log('  3. 运行 npm run dev 启动开发');
} else {
  console.log('❌ 部分检查未通过，请根据上述提示修复问题。');
  console.log('\n常见解决方案：');
  console.log('  - 运行 npm install 安装依赖');
  console.log('  - 添加 src/common/logo.png 图标文件');
  console.log('  - 确保在项目根目录运行此脚本');
}

console.log('='.repeat(60) + '\n');

process.exit(allPassed ? 0 : 1);
