#!/bin/bash
# 智能投研工作台 - 启动脚本
# Intelligent Investment Research Workbench - Startup Script

echo "========================================"
echo "  智能投研工作台启动器"
echo "  Intelligent Investment Research Workbench"
echo "========================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查Python环境
echo "[1/4] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python版本: $PYTHON_VERSION"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo ""
    echo "[2/4] 创建虚拟环境..."
    python3 -m venv venv
    echo "✓ 虚拟环境创建完成"
else
    echo ""
    echo "[2/4] 虚拟环境已存在"
fi

# 激活虚拟环境
echo ""
echo "[3/4] 激活虚拟环境并安装依赖..."
source venv/bin/activate

# 升级pip
pip install --upgrade pip -q

# 安装依赖
echo "正在安装依赖（可能需要几分钟）..."
pip install -r app_requirements.txt -q

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败，尝试使用国内镜像..."
    pip install -r app_requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q
fi

echo "✓ 依赖安装完成"

# 检查环境变量
echo ""
echo "[4/4] 检查API配置..."

if [ -z "$TUSHARE_TOKEN" ]; then
    echo "⚠️  警告: 未设置 TUSHARE_TOKEN"
    echo "    部分功能（A股财务分析）将不可用"
    echo "    设置方法: export TUSHARE_TOKEN='your_token'"
else
    echo "✓ Tushare Token 已配置"
fi

if [ -z "$TIANYANCHA_TOKEN" ]; then
    echo "⚠️  警告: 未设置 TIANYANCHA_TOKEN"
    echo "    部分功能（工商信息查询）将不可用"
    echo "    设置方法: export TIANYANCHA_TOKEN='your_token'"
else
    echo "✓ 天眼查 Token 已配置"
fi

# 启动应用
echo ""
echo "========================================"
echo "✓ 准备就绪，正在启动应用..."
echo "========================================"
echo ""
echo "应用将在浏览器中自动打开"
echo "如果未自动打开，请手动访问: http://localhost:8501"
echo ""
echo "按 Ctrl+C 停止应用"
echo ""

# 启动Streamlit
streamlit run app.py --server.port=8501 --server.address=localhost

# 停用虚拟环境（脚本结束时）
deactivate
