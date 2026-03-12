#!/bin/bash
# 收并购分析套件 - 导出脚本
# 将套件打包导出，方便迁移到其他设备

set -e

VERSION="1.0.0"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
EXPORT_NAME="ma-analysis-kit-v${VERSION}-${TIMESTAMP}"

echo "========================================"
echo "  收并购分析套件 - 导出"
echo "  版本: $VERSION"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# 创建导出目录
mkdir -p exports

echo "[1/3] 清理临时文件..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name ".DS_Store" -delete 2>/dev/null || true

echo ""
echo "[2/3] 打包文件..."

# 创建 tar.gz
tar -czvf "exports/${EXPORT_NAME}.tar.gz" \
    --exclude="exports" \
    --exclude=".git" \
    --exclude="projects" \
    --exclude="data" \
    --exclude="report" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude=".DS_Store" \
    .

echo ""
echo "[3/3] 创建 ZIP 格式..."

zip -r "exports/${EXPORT_NAME}.zip" . \
    -x "exports/*" \
    -x ".git/*" \
    -x "projects/*" \
    -x "data/*" \
    -x "report/*" \
    -x "__pycache__/*" \
    -x "*.pyc" \
    -x ".DS_Store"

echo ""
echo "========================================"
echo "✓ 导出完成!"
echo "========================================"
echo ""
echo "导出文件:"
ls -lh exports/
echo ""
echo "文件位置:"
echo "  - exports/${EXPORT_NAME}.tar.gz"
echo "  - exports/${EXPORT_NAME}.zip"
echo ""
echo "使用方法:"
echo "  1. 复制导出文件到目标设备"
echo "  2. 解压: tar -xzvf ${EXPORT_NAME}.tar.gz"
echo "  3. 运行: ./verify.sh"
echo ""
