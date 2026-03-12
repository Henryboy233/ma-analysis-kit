#!/bin/bash
# 演示前检查脚本
# 确保所有功能正常，避免演示翻车

echo "🔍 智能投研工作台 - 演示前检查"
echo "================================"

# 检查应用是否运行
echo ""
echo "1️⃣ 检查应用运行状态..."
if pgrep -f "streamlit run app.py" > /dev/null; then
    echo "   ✅ 应用正在运行"
    PID=$(pgrep -f "streamlit run app.py" | head -1)
    echo "   PID: $PID"
else
    echo "   ⚠️  应用未运行，正在启动..."
    ./start_app.sh &
    sleep 5
fi

# 检查端口
echo ""
echo "2️⃣ 检查端口 8501..."
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   ✅ 端口 8501 正常监听"
else
    echo "   ❌ 端口 8501 未监听"
fi

# 检查网络连接
echo ""
echo "3️⃣ 检查网络连接..."
if ping -c 1 tushare.pro > /dev/null 2>&1; then
    echo "   ✅ 可以连接到 Tushare"
else
    echo "   ⚠️  网络连接可能有问题"
fi

# 检查配置文件
echo ""
echo "4️⃣ 检查配置文件..."
if [ -f "config/.env" ]; then
    echo "   ✅ 配置文件存在"
    if grep -q "TUSHARE_TOKEN=26" config/.env; then
        echo "   ✅ Tushare Token 已配置"
    else
        echo "   ❌ Tushare Token 未配置"
    fi
else
    echo "   ❌ 配置文件不存在"
fi

# 测试API
echo ""
echo "5️⃣ 测试 Tushare API..."
cd ~/ma-analysis-kit
source venv/bin/activate
python3 << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv('config/.env')

token = os.getenv('TUSHARE_TOKEN')
if token:
    import tushare as ts
    ts.set_token(token)
    pro = ts.pro_api()
    try:
        df = pro.daily(ts_code='600519.SH', start_date='20260311', end_date='20260311')
        if not df.empty:
            print("   ✅ API 调用成功")
            print(f"   茅台最新价: ¥{df.iloc[0]['close']}")
        else:
            print("   ⚠️  API 返回空数据")
    except Exception as e:
        print(f"   ❌ API 调用失败: {e}")
else:
    print("   ❌ Token 未配置")
EOF

# 检查邮件配置
echo ""
echo "6️⃣ 检查邮件配置..."
if grep -q "SMTP_SERVER" config/.env 2>/dev/null; then
    echo "   ✅ 邮件配置存在"
else
    echo "   ℹ️  邮件配置可选（演示时手动输入）"
fi

echo ""
echo "================================"
echo "✅ 检查完成！"
echo ""
echo "🌐 访问地址: http://localhost:8501"
echo ""
echo "📋 演示前确认清单:"
echo "  ☐ 浏览器已打开 http://localhost:8501"
echo "  ☐ 页面加载正常"
echo "  ☐ 侧边栏显示 Tushare: 已连接"
echo "  ☐ 准备演示股票代码: 600519.SH"
echo ""
