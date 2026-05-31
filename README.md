# CXin-MiBand

小米手环/手表 Vela OS 应用集合，包含实用工具和学习应用。

## 📱 应用列表

### 1. 手电筒应用 (Flashlight App)

一个功能强大的可编程手电筒应用，支持自定义颜色和可视化编程。

**主要特性：**
- 🎨 RGB 精确颜色调整（0-255全范围）
- 💡 9种预设常用颜色快速选择
- 🎯 可视化编程功能（拖拽式指令管理）
- 🚨 内置默认程序（SOS求救、警车灯、频闪）
- 📝 自定义程序创建和管理
- ⚡ 实时预览和测试功能

**适用场景：**
- 日常照明
- 紧急求救信号
- 创意灯光效果
- 学习编程逻辑

[查看详细文档 →](./flashlight-app/README.md)

### 2. 单词学习应用 (Vocabulary App)

高中英语单词学习应用，支持按教材单元学习。

**主要特性：**
- 📚 完整的高中英语教材词汇（必修+选择性必修）
- 📖 按单元组织，便于同步学习
- 🔄 支持单词浏览和学习
- 💾 本地数据存储，无需网络

**包含教材：**
- 必修第一册、第二册、第三册
- 选择性必修第一册、第二册、第三册、第四册
- 每册5个单元 + Welcome Unit

[查看详细文档 →](./vocabulary-app/README.md)

### 3. 毁灭吧 (Doom App)

复古风格的第一人称射击游戏，带你回到经典游戏时代。

**主要特性：**
- 🎮 3D 射线投射渲染引擎
- 🕹️ 完整的游戏操控（移动、转向、射击）
- 👾 敌人战斗和物资收集
- 🎯 准星瞄准和振动反馈
- 💊 血量和弹药管理系统
- 🗺️ 迷宫探索和通关机制

**游戏玩法：**
- 在迷宫中消灭所有敌人
- 收集弹药和血包补给
- 找到出口完成关卡
- 注意保持血量避免失败

[查看详细文档 →](./doom-app/README.md)

## 🚀 快速开始

### 环境要求

- Node.js >= 14.0.0
- npm >= 6.0.0
- 小米手环/手表（支持 Vela OS）
- 最低平台版本：1070

### 安装依赖

```bash
# 进入具体应用目录
cd flashlight-app
# 或
cd vocabulary-app
# 或
cd doom-app

# 安装依赖
npm install
```

### 开发调试

```bash
# 开发模式（带热更新）
npm run dev

# 或使用 AIoT-toolkit
npx aiot-toolkit start
```

### 构建发布

```bash
# 构建项目
npm run build

# 打包发布
npm run release
```

### 安装到手环

1. 将打包好的 `.rpk` 文件传输到手机
2. 打开小米运动健康 App
3. 进入"设备" → 选择手环 → "应用管理"
4. 点击"添加应用"，选择 `.rpk` 文件
5. 等待安装完成

## 🛠️ 开发工具

### AIoT-toolkit2.0 命令

```bash
# 初始化模拟器环境（首次使用）
npx aiot-toolkit initEmulatorEnv

# 创建虚拟设备
npx aiot-toolkit createVVD

# 查看已连接的设备
npx aiot-toolkit getConnectedDevices

# 查看可用平台
npx aiot-toolkit getPlatforms

# 安装调试器和模拟器
npx aiot-toolkit installDbgAndMkp

# 查看所有命令
npx aiot-toolkit --help
```

### 使用 AIoT IDE

1. 下载并安装 [AIoT IDE](https://aiot.mi.com/)
2. 打开项目文件夹
3. 点击"安装项目依赖"
4. 点击"初始化模拟器环境"
5. 选择设备型号（如小米手环9Pro）
6. 按 F5 开始调试

## 📁 项目结构

```
CXin-MiBand/
├── flashlight-app/          # 手电筒应用
│   ├── src/                 # 源代码
│   ├── dist/                # 构建输出
│   ├── package.json         # 项目配置
│   └── README.md            # 应用文档
├── vocabulary-app/          # 单词学习应用
│   ├── src/                 # 源代码
│   ├── data/                # 词汇数据
│   ├── dist/                # 构建输出
│   ├── package.json         # 项目配置
│   └── README.md            # 应用文档
├── doom-app/                # 毁灭吧游戏
│   ├── src/                 # 源代码
│   ├── dist/                # 构建输出
│   ├── package.json         # 项目配置
│   └── README.md            # 应用文档
├── assets/                  # 共享资源
│   └── images/              # 图片资源
├── scripts/                 # 开发脚本（数据库分析等）
└── README.md                # 本文件
```

## 🎓 技术栈

- **框架**: Vela OS (小米手环/手表操作系统)
- **开发语言**: UX (类Vue语法)
- **构建工具**: AIoT-toolkit2.0
- **API**: Vela System APIs
  - `system.router` - 页面路由
  - `system.brightness` - 亮度控制
  - `system.screen` - 屏幕控制
  - `system.storage` - 本地存储
  - `system.prompt` - 提示对话框
  - `system.app` - 应用控制
  - `system.vibrator` - 振动反馈

## 📚 学习资源

- [Vela OS 官方文档](https://aiot.mi.com/)
- [AIoT 开发者社区](https://aiot.mi.com/community)
- [快应用开发文档](https://doc.quickapp.cn/)

## ⚠️ 注意事项

1. **电量消耗**: 某些功能（如手电筒高亮度模式）会快速消耗电量
2. **兼容性**: 应用需要 Vela OS 1070+ 版本支持
3. **存储限制**: 手环存储空间有限，注意数据大小
4. **性能优化**: 避免复杂动画和大量数据处理
5. **测试**: 建议先在模拟器测试，再安装到实际设备

## 🐛 问题反馈

如果遇到问题或有建议，请：
1. 查看各应用的详细文档
2. 提交 [Issue](https://github.com/ChenXin-2009/CXin-MiBand/issues)
3. 提供设备型号和系统版本信息

## 🔮 未来计划

- [ ] 添加更多实用工具应用
- [ ] 优化现有应用性能
- [ ] 增加应用间数据共享
- [ ] 支持更多设备型号
- [ ] 添加云端同步功能
- [ ] 开发配套手机端应用

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢小米 AIoT 团队提供的开发工具和文档
- 感谢所有测试人员和用户的反馈
- 感谢开源社区的支持

---

**作者**: ChenXin  
**更新日期**: 2026-05-31  
**兼容性**: 小米手环/手表 (Vela OS 1070+)  
**仓库**: https://github.com/ChenXin-2009/CXin-MiBand

