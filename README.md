# apk-builder

一个功能强大的 Android 应用，用于分析和检查 APK 文件结构。

## 特性

- 📦 完整的 APK 解包和分析
- 🔍 APK 文件结构详细检查
- 🖼️ 提取应用资源和图片
- 📋 解析 AndroidManifest.xml
- 🔐 检测潜在的恶意行为特征
- 🎨 简洁的 Kivy Android 用户界面
- 💾 生成详细的分析报告

## 快速开始

### 📱 Android 版本

使用以下方式之一构建 APK：

#### 🚀 方式 1: GitHub Actions (推荐)
```bash
git push origin main
# 然后在 GitHub Actions 中查看构建进度
```

#### 🐳 方式 2: Docker 本地构建
```bash
chmod +x build_apk.sh
./build_apk.sh
```

#### 💻 方式 3: 本地直接构建
```bash
chmod +x build_local.sh
./build_local.sh
```

### 💻 桌面版本

使用 Python 直接运行：
```bash
python main.py
```

## 项目结构

```
.
├── main.py              # 桌面版入口（Tkinter GUI）
├── main_kivy.py         # Android 版入口（Kivy GUI）
├── analyzer.py          # 核心分析引擎
├── buildozer.spec       # Android 构建配置
├── build_apk.sh         # Docker 构建脚本
├── build_local.sh       # 本地构建脚本
└── BUILD_GUIDE_CN.md    # 详细构建指南
```

## 前置要求

### 最小要求
- Python 3.10+
- Git

### 完整要求（用于本地构建）
- Buildozer
- Cython
- Java 11+
- Android SDK & NDK
- Ant, Autotools

或者使用 Docker（更简单）

## 构建指南

详见 [BUILD_GUIDE_CN.md](./BUILD_GUIDE_CN.md)

## APK 安装

构建完成后：
```bash
adb install bin/xingchen-2.0-debug.apk
```

## 使用方式

### Android 版本
1. 启动应用
2. 选择一个 APK 文件
3. 选择分析选项（如提取图片）
4. 查看详细分析结果
5. 导出完整报告

### 桌面版本
```bash
python main.py
```

## 配置

编辑 `buildozer.spec` 自定义：
- 应用名称、包名、版本
- 目标 Android API 级别
- 应用权限
- 依赖包

## 故障排除

### 构建失败
- 检查网络连接（需要下载 SDK/NDK）
- 查看详细构建日志
- 参考 BUILD_GUIDE_CN.md 中的常见问题

### 运行时错误
- 确保已授予必要的存储权限
- 检查 Android 版本兼容性

## 进展状态

- ✅ 核心分析功能
- ✅ Kivy Android UI
- ✅ Docker 构建环境
- ✅ GitHub Actions CI/CD
- ✅ APK 自动化构建
- ⏳ 应用签名和发布

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

详见项目许可证文件。
