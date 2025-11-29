#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "准备将 `main_kivy.py` 作为 Android 入口构建（会临时备份现有 `main.py`）"

if [ ! -f main_kivy.py ]; then
  echo "找不到 main_kivy.py，取消。"
  exit 1
fi

if [ -f main.py ] && [ ! -f main.py.bak_for_build ]; then
  echo "备份现有 main.py -> main.py.bak_for_build"
  mv main.py main.py.bak_for_build
fi

echo "复制 main_kivy.py -> main.py"
cp main_kivy.py main.py

echo "开始 buildozer 构建（可能会很长）"
if command -v docker >/dev/null 2>&1; then
  echo "检测到 docker，使用 kivy/buildozer 镜像（推荐）"
  docker run --rm -v "$PWD":/home/user/hostcwd -w /home/user/hostcwd kivy/buildozer:latest /bin/bash -lc "buildozer -v android debug"
else
  buildozer -v android debug
fi

BUILD_EXIT=$?

echo "构建结束，恢复原始 main.py（如果有备份）"
if [ -f main.py.bak_for_build ]; then
  mv -f main.py.bak_for_build main.py
fi

exit $BUILD_EXIT
#!/usr/bin/env bash
# APK 快速编译脚本

echo "🚀 启动 main.py 到 APK 编译"
echo "=============================="
echo ""

# 检查环境
echo "📋 第一步: 检查编译环境..."
python3 apk_generator.py check
if [ $? -ne 0 ]; then
    echo "❌ 环境检查失败！"
    exit 1
fi

echo ""
echo "✅ 环境检查完毕！"
echo ""

# 显示编译信息
echo "📝 编译信息:"
python3 apk_generator.py info

echo ""
echo "🔨 第二步: 开始编译 APK..."
echo "这可能需要 60-120 分钟，请稍候..."
echo ""

# 开始编译
cd /workspaces/apk-builder
buildozer -v android debug

# 检查编译结果
echo ""
if [ -f "bin/xingchen-2.0-debug.apk" ]; then
    echo "✅ 编译成功！"
    echo ""
    echo "📦 生成的 APK 信息:"
    ls -lh bin/xingchen-2.0-debug.apk
    echo ""
    echo "📱 安装到手机:"
    echo "   adb install bin/xingchen-2.0-debug.apk"
else
    echo "❌ 编译失败！"
    echo "请查看上面的错误信息。"
    exit 1
fi

echo ""
echo "🎉 完成！"
