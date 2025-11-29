#!/usr/bin/env bash
# 简化的本地构建脚本（不使用 Docker）
# 需要已安装 buildozer, cython, 和 Android SDK/NDK

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "=== APK 构建工具 ==="
echo ""

# 检查必要工具
check_tool() {
  if ! command -v "$1" &> /dev/null; then
    echo "❌ 错误: $1 未安装"
    return 1
  fi
  return 0
}

echo "📋 检查依赖..."
check_tool "buildozer" || exit 1
check_tool "java" || exit 1
check_tool "git" || exit 1

echo "✅ 依赖检查完毕"
echo ""

# 准备 Android 入口
echo "📱 准备 Android 入口..."
if [ ! -f main_kivy.py ]; then
  echo "❌ 错误: 找不到 main_kivy.py"
  exit 1
fi

if [ -f main.py ] && [ ! -f main.py.bak_for_build ]; then
  echo "💾 备份原始 main.py -> main.py.bak_for_build"
  mv main.py main.py.bak_for_build
fi

echo "📋 复制 main_kivy.py -> main.py"
cp main_kivy.py main.py

echo ""
echo "🔨 开始构建 APK..."
echo "⏱️  预计需要 30-120 分钟，请耐心等待..."
echo ""

# 运行 buildozer
# 用 (echo y; sleep 3600) 来处理可能的交互式提示
if (echo 'y'; sleep 3600) | buildozer -v android debug; then
  BUILD_SUCCESS=true
else
  BUILD_SUCCESS=false
fi

# 恢复原始 main.py
echo ""
echo "🔄 恢复原始 main.py..."
if [ -f main.py.bak_for_build ]; then
  mv main.py.bak_for_build main.py
  echo "✅ 已恢复"
fi

# 检查结果
echo ""
if [ "$BUILD_SUCCESS" = true ] && [ -f "bin/xingchen-2.0-debug.apk" ]; then
  echo "✅ 构建成功！"
  echo ""
  echo "📦 APK 位置:"
  ls -lh bin/xingchen-2.0-debug.apk
  echo ""
  echo "📱 使用 ADB 安装到手机:"
  echo "   adb install bin/xingchen-2.0-debug.apk"
  exit 0
else
  echo "❌ 构建失败"
  if [ -d bin ]; then
    echo "📁 bin 目录内容:"
    ls -lh bin/ || echo "   (空)"
  fi
  exit 1
fi
