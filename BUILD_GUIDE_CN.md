# 星辰 APK 构建指南

## 概述

本项目是一个 Android APK 应用，用于分析和检查 APK 文件结构。

- **桌面版**: `main.py` (Tkinter GUI)
- **Android 版**: `main_kivy.py` (Kivy UI)
- **核心逻辑**: `analyzer.py` (与 UI 无关的分析函数)

## 快速开始

### 方式 1️⃣: GitHub Actions (推荐 - 云构建)

最简单的方式。只需 push 代码到 GitHub，CI 会自动构建：

```bash
git push origin main
```

然后在 GitHub 上查看：
- 进入 **Actions** 标签页
- 找到 **Build APK** 工作流
- 等待构建完成（约 60-120 分钟）
- 下载 APK artifact

**优点**:
- ✅ 无需本地配置
- ✅ 稳定可靠
- ✅ 自动处理所有依赖
- ✅ 可在任何设备上运行

### 方式 2️⃣: Docker 本地构建

使用 Docker 在本地构建（需要 Docker 已安装）：

```bash
chmod +x build_apk.sh
./build_apk.sh
```

**优点**:
- ✅ 隔离编译环境
- ✅ 无需安装 Android SDK/NDK
- ✅ 快速反馈（本地构建）

**缺点**:
- ❌ 需要 Docker
- ❌ 首次构建较慢

### 方式 3️⃣: 本地直接构建

如果已安装 buildozer, Java, Android SDK/NDK：

```bash
chmod +x build_local.sh
./build_local.sh
```

**优点**:
- ✅ 最快
- ✅ 无额外依赖

**缺点**:
- ❌ 需要复杂的本地环境配置

## 前置要求

### 方式 1 (CI)
- GitHub 账户
- Git

### 方式 2 (Docker)
- Docker
- Git

### 方式 3 (本地)
- Python 3.12+
- Buildozer
- Cython
- Java 11+
- Android SDK (API 21-35)
- Android NDK (版本 25b)
- Git, Ant, Autotools

## 构建输出

成功构建后，APK 文件将位于：
```
bin/xingchen-2.0-debug.apk
```

## 安装到手机

使用 ADB 安装：
```bash
adb install bin/xingchen-2.0-debug.apk
```

## 环境管理

### 重置环境
```bash
chmod +x reset_env.sh
./reset_env.sh
```

### 初始化环境
```bash
chmod +x setup_env.sh
./setup_env.sh
```

## 项目结构

```
.
├── main.py                 # 桌面版入口（Tkinter）
├── main_kivy.py            # Android 版入口（Kivy）
├── analyzer.py             # 核心分析逻辑
├── buildozer.spec          # Buildozer 配置文件
├── build_apk.sh            # Docker 构建脚本
├── build_local.sh          # 本地构建脚本
├── setup_env.sh            # 环境初始化脚本
├── reset_env.sh            # 环境重置脚本
└── .github/workflows/
    └── build-apk.yml       # GitHub Actions 配置
```

## 常见问题

### Q: 构建时间太长了怎么办？
**A**: 这是正常的。首次构建通常需要 60-120 分钟，因为需要下载并编译 NDK、Gradle 等。后续构建会更快。

### Q: 提示 "sdkmanager not found"
**A**: 这是 Android SDK 初始化的一部分。buildozer 会自动下载正确的工具，只需要耐心等待。

### Q: 如何调试构建失败？
**A**: 
- 查看完整的构建日志
- 对于 CI 构建，在 GitHub Actions 中查看完整输出
- 对于本地构建，脚本会输出详细日志

### Q: 可以生成 release 版本吗？
**A**: 是的，修改 `build_apk.sh` 或 `build_local.sh` 中的 `android debug` 改为 `android release`，但需要签名密钥。

## 构建配置

编辑 `buildozer.spec` 来自定义：
- 应用名称和版本
- 权限要求
- 目标 Android API 级别
- 应用图标和启动画面

## 贡献和支持

有问题或改进建议？欢迎提交 Issue 或 Pull Request！

## 许可证

本项目遵循原项目的许可证。
