# 贡献指南

感谢你考虑为 CXin-MiBand 项目做出贡献！

## 如何贡献

### 报告问题

如果你发现了 bug 或有功能建议：

1. 在 [Issues](https://github.com/ChenXin-2009/CXin-MiBand/issues) 页面搜索，确保问题未被报告
2. 创建新的 Issue，使用清晰的标题和详细描述
3. 提供以下信息：
   - 设备型号（如：小米手环9Pro）
   - 系统版本（Vela OS 版本）
   - 应用版本
   - 复现步骤
   - 预期行为和实际行为
   - 截图或日志（如果适用）

### 提交代码

#### 1. Fork 项目

点击 GitHub 页面右上角的 "Fork" 按钮。

#### 2. 克隆仓库

```bash
git clone https://github.com/你的用户名/CXin-MiBand.git
cd CXin-MiBand
```

#### 3. 创建分支

```bash
git checkout -b feature/你的功能名称
# 或
git checkout -b fix/你的修复名称
```

分支命名规范：
- `feature/功能名` - 新功能
- `fix/问题名` - Bug 修复
- `docs/文档名` - 文档更新
- `refactor/重构名` - 代码重构
- `test/测试名` - 测试相关

#### 4. 进行修改

- 遵循现有代码风格
- 添加必要的注释
- 确保代码可以正常构建
- 测试你的修改

#### 5. 提交更改

```bash
git add .
git commit -m "类型: 简短描述

详细描述（可选）
"
```

提交信息格式：
- `feat: 添加新功能`
- `fix: 修复某个问题`
- `docs: 更新文档`
- `style: 代码格式调整`
- `refactor: 代码重构`
- `test: 添加测试`
- `chore: 构建或辅助工具变动`

#### 6. 推送到 GitHub

```bash
git push origin feature/你的功能名称
```

#### 7. 创建 Pull Request

1. 访问你 Fork 的仓库页面
2. 点击 "New Pull Request"
3. 填写 PR 标题和描述
4. 等待审核

### Pull Request 指南

**好的 PR 应该：**
- 有清晰的标题和描述
- 解决一个具体的问题或添加一个具体的功能
- 包含必要的测试
- 更新相关文档
- 保持代码风格一致

**PR 描述应包含：**
- 修改的目的和背景
- 主要改动说明
- 测试情况
- 相关 Issue 编号（如果有）

## 开发规范

### 代码风格

#### JavaScript/UX
- 使用 2 空格缩进
- 使用单引号
- 语句末尾加分号
- 变量命名使用驼峰命名法
- 常量使用大写字母和下划线

#### 文件命名
- 组件文件：`index.ux`
- 配置文件：`manifest.json`
- 脚本文件：`kebab-case.js`

### 目录结构

```
app-name/
├── src/
│   ├── pages/           # 页面组件
│   │   └── page-name/
│   │       └── index.ux
│   ├── common/          # 公共资源
│   ├── data/            # 数据文件
│   ├── manifest.json    # 应用配置
│   └── app.ux          # 应用入口
├── data/                # 原始数据（如CSV）
├── package.json
└── README.md
```

### 提交前检查清单

- [ ] 代码可以正常构建（`npm run build`）
- [ ] 在模拟器或真机上测试过
- [ ] 更新了相关文档
- [ ] 提交信息清晰明确
- [ ] 没有包含不必要的文件（检查 .gitignore）
- [ ] 代码风格符合项目规范

## 开发环境设置

### 必需工具

1. **Node.js** (>= 14.0.0)
   ```bash
   node --version
   ```

2. **AIoT-toolkit**
   ```bash
   npm install -g aiot-toolkit
   ```

3. **AIoT IDE**（可选）
   - 下载：https://aiot.mi.com/

### 初始化项目

```bash
# 安装依赖
cd flashlight-app  # 或 vocabulary-app
npm install

# 初始化模拟器环境
npm run init

# 启动开发服务器
npm run dev
```

## 测试指南

### 手动测试

1. **功能测试**
   - 测试所有主要功能
   - 测试边界情况
   - 测试错误处理

2. **兼容性测试**
   - 在模拟器上测试
   - 在真实设备上测试（如果可能）
   - 测试不同屏幕尺寸

3. **性能测试**
   - 检查响应速度
   - 检查内存使用
   - 检查电量消耗

### 测试报告

在 PR 中说明测试情况：
```
测试环境：
- 设备：小米手环9Pro 模拟器
- 系统：Vela OS 1070
- 应用版本：2.0.0

测试结果：
- [x] 功能正常
- [x] 无明显性能问题
- [x] UI 显示正常
```

## 文档贡献

文档同样重要！你可以：
- 修正错别字和语法错误
- 改进说明的清晰度
- 添加使用示例
- 翻译文档（如果需要）
- 添加截图和演示

## 社区准则

- 尊重所有贡献者
- 保持友好和专业
- 接受建设性批评
- 关注项目目标

## 获取帮助

如果你有任何问题：
1. 查看 [README](./README.md) 和应用文档
2. 搜索现有的 [Issues](https://github.com/ChenXin-2009/CXin-MiBand/issues)
3. 创建新的 Issue 提问

## 许可证

通过贡献代码，你同意你的贡献将在 [MIT License](./LICENSE) 下发布。

---

再次感谢你的贡献！🎉
