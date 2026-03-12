#!/bin/bash
# 收并购分析套件 - 快速开始脚本
# MA Analysis Kit - Quick Start Script

set -e

echo "========================================"
echo "  收并购分析套件 - 快速开始"
echo "  MA Analysis Kit - Quick Start"
echo "========================================"
echo ""

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法: ./QUICKSTART.sh [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  setup       - 安装依赖和配置"
    echo "  init        - 初始化新的分析项目"
    echo "  collect     - 收集数据"
    echo "  analyze     - 生成分析报告"
    echo "  full        - 完整流程 (收集+分析)"
    echo ""
    echo "示例:"
    echo "  ./QUICKSTART.sh setup"
    echo "  ./QUICKSTART.sh init --company \"目标公司\""
    echo "  ./QUICKSTART.sh collect --company \"目标公司\""
    echo "  ./QUICKSTART.sh analyze --company \"目标公司\""
    echo "  ./QUICKSTART.sh full --company \"目标公司\""
    exit 1
fi

COMMAND=$1
shift

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

case $COMMAND in
    setup)
        echo "[1/3] 安装 Python 依赖..."
        pip install -r scripts/requirements.txt
        
        echo ""
        echo "[2/3] 创建数据目录..."
        mkdir -p data report
        
        echo ""
        echo "[3/3] 配置检查..."
        if [ -f "ma-config.json" ]; then
            echo "✓ 配置文件已存在"
        else
            echo "创建默认配置文件..."
            cat > ma-config.json << 'EOF'
{
  "user_profile": {
    "industry_focus": ["TMT", "金融科技", "消费"],
    "investment_stage": "growth",
    "ticket_size": "10-50m",
    "geography": "China"
  },
  "data_sources": {
    "tianyancha_api_key": "",
    "daloopa_token": ""
  },
  "analysis_preferences": {
    "default_valuation_methods": ["DCF", "Comps"],
    "forecast_years": 5,
    "terminal_growth": 0.025
  }
}
EOF
        fi
        
        echo ""
        echo "========================================"
        echo "✓ 安装完成!"
        echo "========================================"
        echo ""
        echo "下一步:"
        echo "  1. 编辑 ma-config.json 配置API密钥"
        echo "  2. 运行: ./QUICKSTART.sh init --company \"目标公司\""
        echo ""
        ;;
        
    init)
        # 解析参数
        COMPANY=""
        while [[ $# -gt 0 ]]; do
            case $1 in
                --company|-c)
                    COMPANY="$2"
                    shift 2
                    ;;
                *)
                    shift
                    ;;
            esac
        done
        
        if [ -z "$COMPANY" ]; then
            echo "错误: 请指定公司名称"
            echo "用法: ./QUICKSTART.sh init --company \"目标公司\""
            exit 1
        fi
        
        echo "初始化分析项目: $COMPANY"
        echo ""
        
        # 创建项目目录
        PROJECT_DIR="projects/$(echo $COMPANY | tr ' ' '_')_$(date +%Y%m%d)"
        mkdir -p "$PROJECT_DIR"/{data,report,docs}
        
        echo "✓ 创建项目目录: $PROJECT_DIR"
        
        # 复制模板
        cp checklists/data-collection.md "$PROJECT_DIR/docs/"
        cp templates/report-template.md "$PROJECT_DIR/docs/"
        
        echo "✓ 复制模板文件"
        
        # 创建项目配置
        cat > "$PROJECT_DIR/project.json" << EOF
{
  "project_name": "$COMPANY 收并购分析",
  "company_name": "$COMPANY",
  "created_date": "$(date -I)",
  "status": "initialized",
  "directories": {
    "data": "$PROJECT_DIR/data",
    "report": "$PROJECT_DIR/report",
    "docs": "$PROJECT_DIR/docs"
  }
}
EOF
        
        echo "✓ 创建项目配置"
        echo ""
        echo "========================================"
        echo "✓ 项目初始化完成!"
        echo "========================================"
        echo ""
        echo "项目目录: $PROJECT_DIR"
        echo ""
        echo "下一步:"
        echo "  1. 收集数据: ./QUICKSTART.sh collect --company \"$COMPANY\""
        echo "  2. 或者查看清单: cat $PROJECT_DIR/docs/data-collection.md"
        echo ""
        ;;
        
    collect)
        COMPANY=""
        while [[ $# -gt 0 ]]; do
            case $1 in
                --company|-c)
                    COMPANY="$2"
                    shift 2
                    ;;
                *)
                    shift
                    ;;
            esac
        done
        
        if [ -z "$COMPANY" ]; then
            echo "错误: 请指定公司名称"
            exit 1
        fi
        
        echo "收集数据: $COMPANY"
        echo ""
        
        # 查找项目目录
        PROJECT_DIR=$(find projects -maxdepth 1 -name "*$(echo $COMPANY | tr ' ' '_')*" -type d | head -1)
        
        if [ -z "$PROJECT_DIR" ]; then
            echo "未找到项目目录，请先运行 init 命令"
            exit 1
        fi
        
        # 运行数据采集
        python3 scripts/data_collector.py \
            --company "$COMPANY" \
            --output "$PROJECT_DIR/data" \
            --sources all
        
        echo ""
        echo "✓ 数据采集完成"
        echo "数据保存在: $PROJECT_DIR/data"
        ;;
        
    analyze)
        COMPANY=""
        while [[ $# -gt 0 ]]; do
            case $1 in
                --company|-c)
                    COMPANY="$2"
                    shift 2
                    ;;
                *)
                    shift
                    ;;
            esac
        done
        
        if [ -z "$COMPANY" ]; then
            echo "错误: 请指定公司名称"
            exit 1
        fi
        
        echo "生成分析报告: $COMPANY"
        echo ""
        
        # 查找项目目录
        PROJECT_DIR=$(find projects -maxdepth 1 -name "*$(echo $COMPANY | tr ' ' '_')*" -type d | head -1)
        
        if [ -z "$PROJECT_DIR" ]; then
            echo "未找到项目目录，请先运行 init 命令"
            exit 1
        fi
        
        # 运行报告生成
        python3 scripts/report_generator.py \
            --input "$PROJECT_DIR/data" \
            --template templates/report-template.md \
            --output "$PROJECT_DIR/report" \
            --company "$COMPANY" \
            --format all
        
        echo ""
        echo "========================================"
        echo "✓ 分析报告生成完成!"
        echo "========================================"
        echo ""
        echo "报告位置: $PROJECT_DIR/report/"
        echo ""
        ls -lh "$PROJECT_DIR/report/"
        ;;
        
    full)
        COMPANY=""
        while [[ $# -gt 0 ]]; do
            case $1 in
                --company|-c)
                    COMPANY="$2"
                    shift 2
                    ;;
                *)
                    shift
                    ;;
            esac
        done
        
        if [ -z "$COMPANY" ]; then
            echo "错误: 请指定公司名称"
            exit 1
        fi
        
        echo "========================================"
        echo "  开始完整分析流程"
        echo "  目标公司: $COMPANY"
        echo "========================================"
        echo ""
        
        # Step 1: Init
        echo "[步骤 1/4] 初始化项目..."
        $0 init --company "$COMPANY"
        
        # Step 2: Collect
        echo ""
        echo "[步骤 2/4] 收集数据..."
        $0 collect --company "$COMPANY"
        
        # Step 3: Analyze
        echo ""
        echo "[步骤 3/4] 生成报告..."
        $0 analyze --company "$COMPANY"
        
        # Step 4: Summary
        echo ""
        echo "[步骤 4/4] 完成汇总"
        PROJECT_DIR=$(find projects -maxdepth 1 -name "*$(echo $COMPANY | tr ' ' '_')*" -type d | head -1)
        
        echo ""
        echo "========================================"
        echo "✓ 完整分析流程完成!"
        echo "========================================"
        echo ""
        echo "项目目录: $PROJECT_DIR"
        echo ""
        echo "输出文件:"
        find "$PROJECT_DIR" -type f -name "*.md" -o -name "*.xlsx" -o -name "*.png" | head -20
        echo ""
        ;;
        
    *)
        echo "错误: 未知命令 '$COMMAND'"
        echo "运行 ./QUICKSTART.sh 查看用法"
        exit 1
        ;;
esac
