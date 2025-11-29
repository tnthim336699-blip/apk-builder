#!/usr/bin/env bash
set -euo pipefail

echo "⚠️  将重置工作区：保留 git 受控的源码文件，删除所有未追踪文件与构建产物。"
echo "    如果你有未提交的更改，请先备份或提交。"
read -p "确认要继续重置吗？输入 'yes' 继续：" CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "取消。未作更改。"
    exit 0
fi

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "-- 重置 git 修改到 HEAD"
git reset --hard HEAD || true

echo "-- 删除未追踪文件和目录 (git clean -fdx)"
git clean -fdx || true

echo "-- 删除常见构建产物与虚拟环境（如果存在）"
rm -rf .buildozer build bin dist tmp .gradle .cache buildozer-* \
       .venv venv venv3 env env3 .pytest_cache || true

echo "-- 清理完成。工作区已重置为 git HEAD（只保留受控源码）。"
echo "请检出 `git status` 确认。"

exit 0
#!/usr/bin/env bash
set -euo pipefail

echo "⚠️  将重置工作区：保留 git 受控的源码文件，删除所有未追踪文件与构建产物。"
echo "    如果你有未提交的更改，请先备份或提交。"
read -p "确认要继续重置吗？输入 'yes' 继续：" CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "取消。未作更改。"
    exit 0
fi

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "-- 重置 git 修改到 HEAD"
git reset --hard HEAD || true

echo "-- 删除未追踪文件和目录 (git clean -fdx)"
git clean -fdx || true

echo "-- 删除常见构建产物与虚拟环境（如果存在）"
rm -rf .buildozer build bin dist tmp .gradle .cache buildozer-* \
       .venv venv venv3 env env3 .pytest_cache || true

echo "-- 清理完成。工作区已重置为 git HEAD（只保留受控源码）。"
echo "请检出 `git status` 确认。"

exit 0
