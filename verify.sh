#!/bin/bash
# 收并购分析套件 - 验证脚本
# 检查套件完整性和环境配置

echo "========================================"
echo "  收并购分析套件 - 完整性验证"
echo "========================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

ERRORS=0
WARNINGS=0

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "[1/5] 检查必需文件..."
echo ""

REQUIRED_FILES=(
    "README.md"
    "WORKFLOW.md"
    "MIGRATION.md"
    "QUICKSTART.sh"
    "skills/ma-analysis/SKILL.md"
    "templates/report-template.md"
    "checklists/data-collection.md"
    "scripts/data_collector.py"
    "scripts/report_generator.py"
    "scripts/requirements.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (缺失)"
        ((ERRORS++))
    fi
done

echo ""
echo "[2/5] 检查 Python 环境..."
echo ""

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python 已安装: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python3 未安装"
    ((ERRORS++))
fi

echo ""
echo "[3/5] 检查 Python 依赖..."
echo ""

if [ -f "scripts/requirements.txt" ]; then
    while IFS= read -r package || [[ -n "$package" ]]; do
        # 跳过注释和空行
        [[ "$package" =~ ^#.*$ ]] && continue
        [[ -z "$package" ]] && continue
        
        # 提取包名 (去掉版本号)
        pkg_name=$(echo "$package" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1)
        
        if python3 -c "import $pkg_name" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} $pkg_name"
        else
            echo -e "${YELLOW}!${NC} $pkg_name (未安装)"
            ((WARNINGS++))
        fi
    done < "scripts/requirements.txt"
fi

echo ""
echo "[4/5] 检查脚本权限..."
echo ""

SCRIPTS=(
    "QUICKSTART.sh"
    "scripts/data_collector.py"
    "scripts/report_generator.py"
)

for script in "${SCRIPTS[@]}"; do
    if [ -x "$script" ]; then
        echo -e "${GREEN}✓${NC} $script 可执行"
    else
        echo -e "${YELLOW}!${NC} $script 缺少执行权限"
        echo "  修复: chmod +x $script"
        ((WARNINGS++))
    fi
done

echo ""
echo "[5/5] 检查 AI 工具集成..."
echo ""

# 检查 Claude Code
if command -v claude &> /dev/null; then
    echo -e "${GREEN}✓${NC} Claude Code 已安装"
    if [ -d "$HOME/.claude/skills/ma-analysis" ]; then
        echo -e "  ${GREEN}✓${NC} Skill 已安装到 Claude Code"
    else
        echo -e "  ${YELLOW}!${NC} Skill 未安装到 Claude Code"
        echo "    安装: cp -r skills/ma-analysis ~/.claude/skills/"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}!${NC} Claude Code 未安装 (可选)"
fi

# 检查 Kimi Code
if command -v kimi &> /dev/null; then
    echo -e "${GREEN}✓${NC} Kimi Code 已安装"
    if [ -d "$HOME/.kimi/skills/ma-analysis" ]; then
        echo -e "  ${GREEN}✓${NC} Skill 已安装到 Kimi Code"
    else
        echo -e "  ${YELLOW}!${NC} Skill 未安装到 Kimi Code"
        echo "    安装: cp -r skills/ma-analysis ~/.kimi/skills/"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}!${NC} Kimi Code 未安装 (可选)"
fi

echo ""
echo "========================================"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ 验证通过! 套件已就绪${NC}"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}! 验证完成，有 $WARNINGS 个警告${NC}"
    echo "  警告不影响基本使用，但建议修复"
else
    echo -e "${RED}✗ 验证失败，有 $ERRORS 个错误${NC}"
    echo "  请修复错误后重新运行验证"
fi

echo "========================================"
echo ""

# 显示下一步
echo "下一步:"
if [ $ERRORS -gt 0 ]; then
    echo "  1. 安装缺失的依赖: pip install -r scripts/requirements.txt"
    echo "  2. 修复文件权限: chmod +x QUICKSTART.sh scripts/*.py"
else
    echo "  1. 快速开始: ./QUICKSTART.sh setup"
    echo "  2. 创建项目: ./QUICKSTART.sh init --company \"目标公司\""
    echo "  3. 查看文档: cat README.md"
fi
echo ""

exit $ERRORS
