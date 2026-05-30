# Vela测试应用

一个最简单的小米手环Vela应用，打开后显示"测试"两个字。

## 项目结构

```
vela-test-app/
├── src/
│   ├── manifest.json          # 应用配置文件
│   ├── app.ux                 # 应用入口
│   ├── pages/
│   │   └── index/
│   │       └── index.ux       # 首页（显示"测试"）
│   └── common/
│       └── logo.png           # 应用图标（需要自己添加）
├── package.json               # npm配置
└── README.md                  # 说明文档
```

## 环境要求

- Node.js >= 14.0.0
- npm >= 6.0.0

## 安装依赖

```bash
npm install
```

这将自动安装 AIoT-toolkit2.0 (v2.0.5) 及其所有依赖。

## 如何使用

### 方法1：使用 AIoT-toolkit2.0 命令行工具（推荐）

#### 1. 初始化模拟器环境（首次使用）

```bash
npx aiot-toolkit initEmulatorEnv
```

按照提示选择设备型号（如小米手环9Pro）。

#### 2. 创建虚拟设备（可选）

```bash
npx aiot-toolkit createVVD
```

#### 3. 开发模式（带热更新）

```bash
npm run dev
# 或
npx aiot-toolkit start
```

这将启动开发服务器，支持热更新。

#### 4. 构建项目

```bash
npm run build
# 或
npx aiot-toolkit build
```

#### 5. 打包发布

```bash
npm run release
# 或
npx aiot-toolkit release
```

打包后的 .rpk 文件位于：`dist/com.test.simple.rpk`

#### 其他有用的命令

```bash
# 查看已连接的设备
npx aiot-toolkit getConnectedDevices

# 查看可用平台
npx aiot-toolkit getPlatforms

# 安装调试器和模拟器
npx aiot-toolkit installDbgAndMkp

# 删除虚拟设备
npx aiot-toolkit deleteVVD

# 查看所有命令
npx aiot-toolkit --help
```

### 方法2：使用 AIoT IDE

1. 下载并安装 AIoT IDE
2. 打开 AIoT IDE
3. 点击"文件" → "打开文件夹"，选择本项目目录
4. 点击右侧辅助栏的"安装项目依赖"按钮
5. 点击"初始化模拟器环境"按钮
6. 选择设备型号（如小米手环9Pro）
7. 按 F5 或点击"调试"按钮
8. 在右侧模拟器中查看效果

## 安装到手环

1. 将打包好的.rpk文件传输到手机
2. 打开小米运动健康App
3. 进入"设备" → 选择手环 → "应用管理"
4. 点击"添加应用"，选择.rpk文件
5. 等待安装完成

## 添加应用图标

在 `src/common/` 目录下添加一个名为 `logo.png` 的图标文件。

**图标要求：**
- 文件名：logo.png
- 尺寸：建议 192x192 像素
- 格式：PNG（支持透明背景）
- 位置：`src/common/logo.png`

如果暂时没有图标，可以：
1. 使用任意 PNG 图片重命名为 `logo.png`
2. 或者在线生成一个简单图标
3. 或者使用设计工具创建一个

**临时解决方案：**
如果只是测试，可以从网上下载任意 PNG 图片，重命名为 `logo.png` 并放到 `src/common/` 目录。

- 黑色背景
- 白色大字显示"测试"
- 文字居中显示
- 适配所有Vela设备

## 技术要点

- 使用了最基础的Vela框架结构
- template中有根div包裹
- CSS使用了position: absolute
- 使用background-color而非background

## 下一步

可以在此基础上添加：
- 按钮交互
- 页面跳转
- 数据存储
- 传感器读取
- 网络请求

## 许可证

MIT License
