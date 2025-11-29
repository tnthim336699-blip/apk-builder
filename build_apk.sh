#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "准备将 main_kivy.py 作为 Android 入口构建（会临时备份现有 main.py ）"

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
  # 直接以 buildozer 命令作为容器命令，避免依赖 /bin/bash 作为入口
  # 为避免容器对宿主文件做 chown（可能无权限），先把源码复制到临时目录（排除 .venv/.git 等），
  # 在临时目录内运行容器构建，构建产物会复制回宿主仓库。
  BUILD_TMP=$(mktemp -d)
  echo "创建临时构建目录: $BUILD_TMP"
  # 使用 rsync 风格复制，排除大型/宿主敏感目录
  rsync -a --exclude='.venv' --exclude='.git' --exclude='.buildozer' --exclude='bin' --exclude='dist' --exclude='build' --exclude='*.zip' ./ "$BUILD_TMP/"

  echo "在临时目录中运行 buildozer..."
  # buildozer.spec 中已设置 warn_on_root = 0，所以不需要管道确认
  # 通过创建许可证接受文件来自动接受 SDK 许可证
  docker run --rm -v "$BUILD_TMP":/work -w /work --entrypoint /bin/bash kivy/buildozer:latest -c "
    mkdir -p /root/.android
    touch /root/.android/repositories.cfg
    mkdir -p /root/.buildozer/android/platform/android-sdk/licenses
    echo 'android-sdk-license' > /root/.buildozer/android/platform/android-sdk/licenses/android-sdk-license
    echo '24333f8a63b6825ea9c5514f83c2829b004d48246d8a1186ae5054fe7ee979c8' >> /root/.buildozer/android/platform/android-sdk/licenses/android-sdk-license
    buildozer -v android debug
  "

  echo "构建完成，复制产物回仓库（如果有）"
  mkdir -p bin
  if [ -d "$BUILD_TMP/bin" ]; then
    cp -a "$BUILD_TMP/bin/"* bin/ || true
  fi

  # 清理临时目录
  rm -rf "$BUILD_TMP"
else
  buildozer -v android debug
fi
