#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "🔧 准备重建开发环境"

# List of recommended apt packages for Buildozer / p4a native builds
APT_PKGS=(
  git build-essential python3-venv python3-pip python3-setuptools python3-wheel 
  autoconf automake libtool libltdl-dev pkg-config libffi-dev libc6-dev libssl-dev 
  openjdk-17-jdk unzip zip ccache
)

install_system_deps() {
  if [ "$(id -u)" -ne 0 ]; then
    echo "注意：当前非 root，跳过 apt 安装。若需要安装系统依赖，请以 root 或使用 sudo 运行此脚本。"
    echo "可运行如下命令来安装（Ubuntu/Debian）："
    echo "  sudo apt update && sudo apt install -y ${APT_PKGS[*]}"
    return 1
  fi

  echo "正在安装系统依赖（apt）..."
  apt update
  apt install -y "${APT_PKGS[@]}"
}

create_venv_and_install_python_deps() {
  echo "创建并激活虚拟环境 .venv"
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate

  echo "升级 pip 并安装 Python 包: buildozer, cython"
  pip install --upgrade pip setuptools wheel
  pip install cython
  pip install --upgrade buildozer

  if [ -f requirements.txt ]; then
    echo "安装 requirements.txt"
    pip install -r requirements.txt
  fi

  echo "虚拟环境已准备：.venv"
}

echo "1) 尝试安装系统依赖（如果有权限）"
install_system_deps || true

echo "2) 创建 Python 虚拟环境并安装 Python 依赖"
create_venv_and_install_python_deps

echo "完成：环境已重建（若需要 Android SDK/NDK，请参照 README 安装或使用 docker/kivy/buildozer 镜像）。"
echo "建议接下来的步骤："
echo "  - 激活虚拟环境： source .venv/bin/activate"
echo "  - 运行构建： ./build_apk.sh  或 在 docker 中运行它 (推荐)"

exit 0
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "🔧 准备重建开发环境"

# List of recommended apt packages for Buildozer / p4a native builds
APT_PKGS=(
  git build-essential python3-venv python3-pip python3-setuptools python3-wheel 
  autoconf automake libtool libltdl-dev pkg-config libffi-dev libc6-dev libssl-dev 
  openjdk-17-jdk unzip zip ccache
)

install_system_deps() {
  if [ "$(id -u)" -ne 0 ]; then
    echo "注意：当前非 root，跳过 apt 安装。若需要安装系统依赖，请以 root 或使用 sudo 运行此脚本。"
    echo "可运行如下命令来安装（Ubuntu/Debian）："
    echo "  sudo apt update && sudo apt install -y ${APT_PKGS[*]}"
    return 1
  fi

  echo "正在安装系统依赖（apt）..."
  apt update
  apt install -y "${APT_PKGS[@]}"
}

create_venv_and_install_python_deps() {
  echo "创建并激活虚拟环境 .venv"
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate

  echo "升级 pip 并安装 Python 包: buildozer, cython"
  pip install --upgrade pip setuptools wheel
  pip install cython
  pip install --upgrade buildozer

  if [ -f requirements.txt ]; then
    echo "安装 requirements.txt"
    pip install -r requirements.txt
  fi

  echo "虚拟环境已准备：.venv"
}

echo "1) 尝试安装系统依赖（如果有权限）"
install_system_deps || true

echo "2) 创建 Python 虚拟环境并安装 Python 依赖"
create_venv_and_install_python_deps

echo "完成：环境已重建（若需要 Android SDK/NDK，请参照 README 安装或使用 docker/kivy/buildozer 镜像）。"
echo "建议接下来的步骤："
echo "  - 激活虚拟环境： source .venv/bin/activate"
echo "  - 运行构建： ./build_apk.sh  或 在 docker 中运行它 (推荐)"

exit 0
