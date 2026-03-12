#!/bin/bash
# 智能投研工作台 - 打包分发脚本
# 用于将项目打包，方便部署到其他服务器

set -e

echo "📦 开始打包智能投研工作台..."

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PACKAGE_NAME="ma-analysis-kit-v2.0"
PACKAGE_DIR="/tmp/${PACKAGE_NAME}"

echo "📁 项目目录: $PROJECT_DIR"
echo "📦 打包目录: $PACKAGE_DIR"

# 清理旧文件
rm -rf "$PACKAGE_DIR"
rm -f "/tmp/${PACKAGE_NAME}.tar.gz"

# 创建打包目录
mkdir -p "$PACKAGE_DIR"

# 复制核心文件
echo "📋 复制核心文件..."
cp -r "$PROJECT_DIR/apis" "$PACKAGE_DIR/"
cp -r "$PROJECT_DIR/config" "$PACKAGE_DIR/"
cp -r "$PROJECT_DIR/skills" "$PACKAGE_DIR/"
cp -r "$PROJECT_DIR/templates" "$PACKAGE_DIR/"
cp -r "$PROJECT_DIR/checklists" "$PACKAGE_DIR/"

# 复制主程序
cp "$PROJECT_DIR/app.py" "$PACKAGE_DIR/"
cp "$PROJECT_DIR/app_requirements.txt" "$PACKAGE_DIR/"
cp "$PROJECT_DIR/start_app.sh" "$PACKAGE_DIR/"

# 复制文档
cp "$PROJECT_DIR/README.md" "$PACKAGE_DIR/"
cp "$PROJECT_DIR/QUICKSTART.md" "$PACKAGE_DIR/"
cp "$PROJECT_DIR/USER_GUIDE.md" "$PACKAGE_DIR/"
cp "$PROJECT_DIR/DEPLOY_GUIDE.md" "$PACKAGE_DIR/"

# 创建示例配置文件
if [ ! -f "$PACKAGE_DIR/config/.env" ]; then
    echo "⚙️ 创建示例配置文件..."
    cat > "$PACKAGE_DIR/config/.env.example" << 'EOF'
# Tushare API Token（免费获取：https://tushare.pro/register）
TUSHARE_TOKEN=your_tushare_token_here

# 天眼查 API Token（可选，购买：https://open.tianyancha.com/recharge/1）
TIANYANCHA_TOKEN=

# 且慢 MCP API Key（已内置）
QIEMAN_API_KEY=zpST_gOMgBPniZGnrHtIaQ

# 邮件配置（可选）
SMTP_SERVER=smtp.163.com
SMTP_PORT=465
SENDER_EMAIL=your_email@163.com
SENDER_PASSWORD=your_auth_code
EOF
fi

# 创建部署说明
cat > "$PACKAGE_DIR/INSTALL.md" << 'EOF'
# 快速安装说明

## 1. 解压
```bash
tar -xzvf ma-analysis-kit-v2.0.tar.gz
cd ma-analysis-kit-v2.0
```

## 2. 安装依赖
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r app_requirements.txt
```

## 3. 配置API
```bash
cp config/.env.example config/.env
# 编辑 config/.env，填入你的Tushare Token
```

## 4. 启动
```bash
./start_app.sh
```

## 5. 访问
浏览器打开：http://localhost:8501

---
详细说明见：DEPLOY_GUIDE.md
EOF

# 打包
echo "📦 创建压缩包..."
cd /tmp
tar -czvf "${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"

# 复制到桌面
cp "/tmp/${PACKAGE_NAME}.tar.gz" "$PROJECT_DIR/"

echo ""
echo "✅ 打包完成！"
echo "📦 文件位置: $PROJECT_DIR/${PACKAGE_NAME}.tar.gz"
echo ""
echo "📋 包内文件列表:"
tar -tzf "$PROJECT_DIR/${PACKAGE_NAME}.tar.gz" | head -30
echo ""
echo "🚀 分发方式:"
echo "  1. 复制 tar.gz 文件到目标服务器"
echo "  2. 解压: tar -xzvf ma-analysis-kit-v2.0.tar.gz"
echo "  3. 按 INSTALL.md 说明部署"
echo ""
