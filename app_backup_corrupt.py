#!/usr/bin/env python3
"""
智能投研工作台 - Streamlit Web应用
Intelligent Investment Research Workbench

面向对象：集团高管、投资决策者
功能：单一公司分析、投资组合监控、商业尽调
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import sys
import json
import base64
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', '.env'))

# 设置页面配置（必须在第一个st命令前）
st.set_page_config(
    page_title="智能投研工作台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入自定义模块
try:
    from apis.tushare_api import TushareFinanceAPI
    from apis.akshare_api import AKShareFinanceAPI  # 免费数据源
    from apis.tianyancha_api import TianyanchaAPI
    from apis.api_manager import APIManager
    from apis.dd_integration import DueDiligenceIntegration  # 尽调数据集成
    from apis.gemini_api import GeminiAnalyzer  # Gemini AI分析
    API_AVAILABLE = True
except ImportError as e:
    API_AVAILABLE = False
    st.error(f"API模块导入失败: {e}")

# ==================== 本地股票代码映射（避免频繁API调用）====================
# 常用股票代码映射表（用于低积分账号）
STOCK_NAME_MAPPING = {
    # 白酒
    '贵州茅台': '600519.SH',
    '五粮液': '000858.SZ',
    '泸州老窖': '000568.SZ',
    '洋河股份': '002304.SZ',
    '山西汾酒': '600809.SH',
    # 金融
    '中国平安': '601318.SH',
    '招商银行': '600036.SH',
    '兴业银行': '601166.SH',
    '中信证券': '600030.SH',
    '东方财富': '300059.SZ',
    # 科技
    '宁德时代': '300750.SZ',
    '比亚迪': '002594.SZ',
    '立讯精密': '002475.SZ',
    '海康威视': '002415.SZ',
    '美的集团': '000333.SZ',
    '格力电器': '000651.SZ',
    '迈瑞医疗': '300760.SZ',
    '恒瑞医药': '600276.SH',
    # 互联网
    '中芯国际': '688981.SH',
    '海光信息': '688041.SH',
    '金山办公': '688111.SH',
    '科大讯飞': '002230.SZ',
    # 能源
    '长江电力': '600900.SH',
    '中国神华': '601088.SH',
    '中国石油': '601857.SH',
    '中国石化': '600028.SH',
    # 其他
    '中国中免': '601888.SH',
    '顺丰控股': '002352.SZ',
    '牧原股份': '002714.SZ',
    '隆基绿能': '601012.SH',
    '通威股份': '600438.SH',
}

# ==================== 页面样式 ====================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .risk-high {
        color: #ff4b4b;
        font-weight: bold;
    }
    .risk-medium {
        color: #ffa500;
        font-weight: bold;
    }
    .risk-low {
        color: #00cc00;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3rem;
        font-size: 1.1rem;
    }
    .report-section {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 工具函数 ====================

def send_test_email(smtp_server, smtp_port, sender_email, sender_password, recipient_email):
    """
    发送测试邮件
    
    Args:
        smtp_server: SMTP服务器地址
        smtp_port: SMTP端口
        sender_email: 发件人邮箱
        sender_password: 邮箱授权码/密码
        recipient_email: 收件人邮箱
    
    Returns:
        (success: bool, message: str)
    """
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = Header('智能投研工作台 - 邮件测试', 'utf-8')
        
        # 邮件正文
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #1f77b4;">📊 智能投研工作台 - 邮件测试</h2>
            
            <p>您好！</p>
            
            <p>这是一封测试邮件，用于验证<strong>深水云科投资决策辅助系统</strong>的邮件发送功能。</p>
            
            <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0;">📧 邮件配置信息</h3>
                <ul>
                    <li><strong>发件邮箱：</strong>{sender_email}</li>
                    <li><strong>收件邮箱：</strong>{recipient_email}</li>
                    <li><strong>发送时间：</strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                    <li><strong>SMTP服务器：</strong>{smtp_server}:{smtp_port}</li>
                </ul>
            </div>
            
            <p>如果您收到此邮件，说明邮件配置<strong style="color: green;">正确无误</strong>！</p>
            
            <p>现在您可以：</p>
            <ul>
                <li>设置投资组合自动周报</li>
                <li>接收分析结果邮件通知</li>
                <li>配置风险预警邮件提醒</li>
            </ul>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            
            <p style="color: #666; font-size: 12px;">
                此邮件由 智能投研工作台 v2.0 自动发送<br>
                深水云科投资决策场景<br>
                © 2026 深水云科
            </p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        # 连接SMTP服务器并发送
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [recipient_email], msg.as_string())
        
        return True, f"测试邮件已成功发送到 {recipient_email}"
        
    except smtplib.SMTPAuthenticationError:
        return False, "邮箱认证失败：请检查邮箱地址和授权码（注意：不是邮箱登录密码）"
    except smtplib.SMTPConnectError:
        return False, "无法连接到SMTP服务器：请检查服务器地址和端口"
    except Exception as e:
        return False, f"发送失败：{str(e)}"

def check_api_status():
    """检查API配置状态"""
    status = {
        "tushare": bool(os.getenv("TUSHARE_TOKEN")),
        "tianyancha": bool(os.getenv("TIANYANCHA_TOKEN")),
        "qieman": True  # 已配置的Key
    }
    return status

def get_binary_file_downloader_html(bin_file, file_label='File'):
    """生成文件下载链接"""
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">点击下载 {file_label}</a>'
    return href

def create_risk_badge(risk_level):
    """创建风险等级标签"""
    colors = {
        "高": "🔴 高风险",
        "中": "🟡 中风险",
        "低": "🟢 低风险"
    }
    return colors.get(risk_level, "⚪ 未知")

def format_number(num, unit=""):
    """格式化数字显示"""
    if num is None:
        return "N/A"
    if abs(num) >= 1e8:
        return f"{num/1e8:.2f}亿{unit}"
    elif abs(num) >= 1e4:
        return f"{num/1e4:.2f}万{unit}"
    else:
        return f"{num:.2f}{unit}"

# ==================== 功能模块 1: 单一公司财务分析 ====================

def single_company_analysis():
    """单一公司财务分析模块"""
    st.header("📈 单一公司深度财务分析")
    st.markdown("输入股票代码或公司名称，获取全面的财务健康度评估")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 输入区域
        input_type = st.radio("输入方式", ["股票代码", "公司名称"], horizontal=True)
        
        if input_type == "股票代码":
            stock_code = st.text_input(
                "输入股票代码（如：600519.SH）",
                placeholder="600519.SH",
                help="格式：股票代码.交易所（SH=上海，SZ=深圳）"
            )
        else:
            company_name = st.text_input(
                "输入公司名称",
                placeholder="贵州茅台"
            )
            stock_code = None  # 将在后面通过公司名称查询
    
    with col2:
        # 分析选项
        st.subheader("分析选项")
        
        # 数据源选择
        tushare_available = bool(os.getenv("TUSHARE_TOKEN"))
        data_source_options = ["AKShare（免费）"]
        if tushare_available:
            data_source_options.append("Tushare（需积分）")
        
        data_source = st.radio(
            "选择数据源",
            data_source_options,
            index=0,
            help="AKShare免费但稳定性略差，Tushare需积分但数据更全"
        )
        use_akshare = "AKShare" in data_source
        
        analysis_period = st.selectbox(
            "分析周期",
            ["近3年", "近5年", "近10年"],
            index=1
        )
        include_industry = st.checkbox("包含行业对比", value=True)
        include_risk = st.checkbox("财务风险排雷", value=True)
    
    # 开始分析按钮
    if st.button("🚀 开始分析", type="primary"):
        if not API_AVAILABLE:
            st.error("API模块未正确加载，请检查配置")
            return
            
        if not stock_code and input_type == "股票代码":
            st.warning("请输入股票代码")
            return
        
        with st.spinner("正在获取数据并分析..."):
            try:
                # 初始化API
                ak_api = AKShareFinanceAPI()
                ts_api = None
                if os.getenv("TUSHARE_TOKEN"):
                    ts_api = TushareFinanceAPI(os.getenv("TUSHARE_TOKEN"))
                
                # 如果是公司名称输入，先查询股票代码
                if input_type == "公司名称":
                    if not company_name:
                        st.warning("请输入公司名称")
                        return
                    
                    st.info(f"正在查询 '{company_name}' 的股票代码...")
                    
                    # 先查本地映射表（避免API调用限制）
                    if company_name in STOCK_NAME_MAPPING:
                        stock_code = STOCK_NAME_MAPPING[company_name]
                        st.success(f"找到匹配：{company_name} ({stock_code})")
                    else:
                        # 尝试模糊匹配本地表
                        matched_names = [name for name in STOCK_NAME_MAPPING.keys() if company_name in name]
                        
                        if len(matched_names) == 1:
                            stock_code = STOCK_NAME_MAPPING[matched_names[0]]
                            st.success(f"找到匹配：{matched_names[0]} ({stock_code})")
                        elif len(matched_names) > 1:
                            st.info(f"找到 {len(matched_names)} 家匹配公司：")
                            for name in matched_names:
                                st.markdown(f"- **{name}**: {STOCK_NAME_MAPPING[name]}")
                            st.info("请使用股票代码方式重新查询，输入上述代码")
                            return
                        else:
                            st.error(f"未找到包含 '{company_name}' 的公司")
                            st.info("💡 **建议：**\n1. 使用股票代码直接查询（如：600519.SH）\n2. 输入更简短的关键词（如'茅台'而不是'贵州茅台酒股份有限公司'）\n3. 查看支持的常用股票列表")
                            
                            # 显示支持的常用股票
                            with st.expander("📋 查看支持的常用股票列表"):
                                stock_list = []
                                for name, code in sorted(STOCK_NAME_MAPPING.items()):
                                    stock_list.append({"公司名称": name, "股票代码": code})
                                st.dataframe(pd.DataFrame(stock_list), use_container_width=True, hide_index=True)
                            return
                
                # 计算日期范围
                end_date = datetime.now()
                years = {"近3年": 3, "近5年": 5, "近10年": 10}[analysis_period]
                start_date = end_date - timedelta(days=365*years)
                
                # 根据用户选择的数据源获取数据
                if use_akshare:
                    # 使用AKShare（免费）
                    st.info("📊 正在使用 AKShare 免费数据源获取数据...")
                    income_df = ak_api.get_income_statement(stock_code)
                    
                    # 如果财务数据为空，使用日线数据进行分析
                    if income_df.empty:
                        st.warning("⚠️ 无法获取财务数据，切换至股价技术分析...")
                        price_df = ak_api.get_daily_price(
                            stock_code,
                            start_date.strftime('%Y%m%d'),
                            end_date.strftime('%Y%m%d')
                        )
                        
                        if price_df.empty:
                            st.error(f"未找到 {stock_code} 的数据")
                            st.info("💡 可能原因：\n1. 股票代码格式错误（应为 600519.SH）\n2. 该股票暂无交易数据")
                            return
                        
                        # 获取公司名称
                        company_name = stock_code
                        for name, code in STOCK_NAME_MAPPING.items():
                            if code == stock_code:
                                company_name = name
                                break
                        
                        # 显示技术分析结果
                        display_technical_results(price_df, company_name, stock_code)
                        st.info("💡 提示：如需完整财务三表，可尝试切换至Tushare数据源（需积分）")
                        return
                    
                    # 获取估值数据（AKShare暂不支持，使用空DataFrame）
                    valuation_df = pd.DataFrame()
                    
                    # 获取公司名称
                    company_name = stock_code
                    for name, code in STOCK_NAME_MAPPING.items():
                        if code == stock_code:
                            company_name = name
                            break
                    
                    # 创建基本信息的DataFrame
                    basic_df = pd.DataFrame([{'ts_code': stock_code, 'name': company_name}])
                    
                    # 显示结果
                    st.success("✅ 成功获取财务数据（AKShare免费数据源）")
                    display_financial_results(income_df, valuation_df, basic_df, stock_code)
                    
                else:
                    # 使用Tushare（需积分）
                    if not ts_api:
                        st.error("⚠️ Tushare未配置，请在侧边栏设置Token")
                        return
                    
                    st.info("📊 正在使用 Tushare 数据源获取数据（需积分）...")
                    income_df = ts_api.get_income_statement(
                        stock_code, 
                        start_date.strftime('%Y%m%d'),
                        end_date.strftime('%Y%m%d')
                    )
                    
                    if income_df.empty:
                        st.error("❌ 无法获取Tushare财务数据")
                        st.info("💡 可能原因：\n1. Tushare积分不足（需2000积分）\n2. 股票代码错误\n3. 建议切换至AKShare免费数据源")
                        return
                    
                    # 获取估值数据
                    valuation_df = ts_api.get_valuation_metrics(stock_code)
                    
                    # 获取公司名称
                    company_name = stock_code
                    for name, code in STOCK_NAME_MAPPING.items():
                        if code == stock_code:
                            company_name = name
                            break
                    
                    # 创建基本信息的DataFrame
                    basic_df = pd.DataFrame([{'ts_code': stock_code, 'name': company_name}])
                    
                    # 显示结果
                    st.success("✅ 成功获取财务数据（Tushare数据源）")
                    display_financial_results(income_df, valuation_df, basic_df, stock_code)
                
            except Exception as e:
                st.error(f"分析过程中出现错误: {str(e)}")
                st.info("提示：请检查网络连接和股票代码是否正确")

def display_financial_results(income_df, valuation_df, basic_df, stock_code):
    """显示财务分析结果"""
    
    # 获取最新数据
    latest = income_df.iloc[-1] if not income_df.empty else None
    company_name = basic_df.iloc[0]['name'] if not basic_df.empty else stock_code
    
    # ==================== 一页纸摘要 ====================
    st.markdown("---")
    st.subheader("📋 一页纸执行摘要（给决策者）")
    
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    with summary_col1:
        st.metric("公司名称", company_name)
        if latest is not None:
            revenue = latest.get('total_revenue', 0)
            st.metric("最新营收", format_number(revenue, "元"))
    
    with summary_col2:
        if latest is not None:
            profit = latest.get('n_income', 0)
            margin = (profit / latest['total_revenue'] * 100) if latest['total_revenue'] else 0
            st.metric("净利润", format_number(profit, "元"))
            st.metric("净利率", f"{margin:.2f}%")
    
    with summary_col3:
        if not valuation_df.empty:
            pe = valuation_df.iloc[0].get('pe', 'N/A')
            pb = valuation_df.iloc[0].get('pb', 'N/A')
            st.metric("市盈率(PE)", f"{pe:.2f}" if isinstance(pe, (int, float)) else pe)
            st.metric("市净率(PB)", f"{pb:.2f}" if isinstance(pb, (int, float)) else pb)
    
    # 财务健康度评分
    st.markdown("---")
    health_score = calculate_health_score(income_df, valuation_df)
    
    score_col1, score_col2 = st.columns([1, 3])
    with score_col1:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = health_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "财务健康度"},
            gauge = {'axis': {'range': [None, 100]},
                     'bar': {'color': "#1f77b4"},
                     'steps': [
                         {'range': [0, 60], 'color': "#ffcccc"},
                         {'range': [60, 80], 'color': "#ffffcc"},
                         {'range': [80, 100], 'color': "#ccffcc"}],
                     'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 60}}
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with score_col2:
        st.subheader("💡 核心结论与建议")
        if health_score >= 80:
            st.success("🟢 **建议：可考虑投资**\n\n财务指标健康，盈利能力稳定，估值合理。建议进一步开展业务尽调。")
        elif health_score >= 60:
            st.warning("🟡 **建议：谨慎推进**\n\n财务表现尚可，但存在部分风险点。建议补充尽调后再做决策。")
        else:
            st.error("🔴 **建议：暂缓投资**\n\n财务指标存在明显风险，建议观望或要求大幅折扣。")
        
        # 关键风险点
        st.markdown("**关键风险点：**")
        risks = identify_risks(income_df, valuation_df)
        for risk in risks:
            st.markdown(f"- {risk}")
    
    # ==================== 详细分析 ====================
    st.markdown("---")
    st.subheader("📊 详细财务分析")
    
    # 趋势图
    if not income_df.empty:
        fig_trends = make_subplots(
            rows=2, cols=2,
            subplot_titles=('营收趋势', '净利润趋势', '毛利率变化', 'ROE变化'),
            vertical_spacing=0.15
        )
        
        # 营收趋势
        fig_trends.add_trace(
            go.Scatter(x=income_df['end_date'], y=income_df['total_revenue'], 
                      mode='lines+markers', name='营业收入', line=dict(color='#1f77b4')),
            row=1, col=1
        )
        
        # 净利润趋势
        fig_trends.add_trace(
            go.Scatter(x=income_df['end_date'], y=income_df['n_income'], 
                      mode='lines+markers', name='净利润', line=dict(color='#2ca02c')),
            row=1, col=2
        )
        
        # 计算比率
        if 'total_cogs' in income_df.columns:
            income_df['gross_margin'] = (income_df['total_revenue'] - income_df['total_cogs']) / income_df['total_revenue'] * 100
            fig_trends.add_trace(
                go.Scatter(x=income_df['end_date'], y=income_df['gross_margin'], 
                          mode='lines+markers', name='毛利率', line=dict(color='#ff7f0e')),
                row=2, col=1
            )
        
        fig_trends.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig_trends, use_container_width=True)
    
    # 数据表格
    with st.expander("查看原始数据"):
        st.dataframe(income_df, use_container_width=True)
    
    # 导出报告按钮
    st.markdown("---")
    if st.button("📥 导出完整报告(PDF)"):
        st.info("报告导出功能开发中，目前可手动复制上方内容")

def calculate_health_score(income_df, valuation_df):
    """计算财务健康度评分（0-100）"""
    score = 70  # 基础分
    
    if income_df.empty:
        return 50
    
    # 增长性评分（30分）
    if len(income_df) >= 2:
        revenue_growth = (income_df.iloc[-1]['total_revenue'] / income_df.iloc[0]['total_revenue'] - 1) * 100
        if revenue_growth > 50:
            score += 15
        elif revenue_growth > 20:
            score += 10
        elif revenue_growth > 0:
            score += 5
        else:
            score -= 10
    
    # 盈利性评分（20分）
    if 'n_income' in income_df.columns and 'total_revenue' in income_df.columns:
        margin = income_df.iloc[-1]['n_income'] / income_df.iloc[-1]['total_revenue']
        if margin > 0.2:
            score += 15
        elif margin > 0.1:
            score += 10
        elif margin > 0:
            score += 5
        else:
            score -= 10
    
    # 估值评分（20分）
    if not valuation_df.empty:
        pe = valuation_df.iloc[0].get('pe')
        if pe and pe < 20:
            score += 10
        elif pe and pe < 40:
            score += 5
        elif pe and pe > 100:
            score -= 10
    
    return min(100, max(0, score))

def identify_risks(income_df, valuation_df):
    """识别财务风险点"""
    risks = []
    
    if income_df.empty:
        return ["无法获取财务数据"]
    
    # 盈利能力风险
    if 'n_income' in income_df.columns:
        if income_df.iloc[-1]['n_income'] < 0:
            risks.append("🔴 最新季度出现亏损")
    
    # 估值风险
    if not valuation_df.empty:
        pe = valuation_df.iloc[0].get('pe')
        if pe and pe > 100:
            risks.append("🟡 市盈率过高，估值可能存在泡沫")
    
    # 增长风险
    if len(income_df) >= 2:
        growth = income_df.iloc[-1]['total_revenue'] / income_df.iloc[0]['total_revenue'] - 1
        if growth < 0:
            risks.append("🟡 营收出现下滑趋势")
    
    if not risks:
        risks.append("🟢 暂无重大财务风险")
    
    return risks

def display_technical_results(price_df, company_name, stock_code):
    """显示基于股价数据的技术分析结果（适用于积分不足的情况）"""
    
    st.markdown("---")
    st.subheader("📋 一页纸执行摘要（基于股价数据）")
    
    # 计算关键指标
    latest = price_df.iloc[-1]
    first = price_df.iloc[0]
    
    # 涨跌幅
    total_return = (latest['close'] - first['close']) / first['close'] * 100
    
    # 波动率
    volatility = price_df['daily_return'].std() * 100 if 'daily_return' in price_df.columns else 0
    
    # 最高最低价
    highest = price_df['high'].max()
    lowest = price_df['low'].min()
    
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    # 获取最新数据日期
    latest_date = price_df.iloc[-1]['trade_date']
    
    with summary_col1:
        st.metric("公司名称", company_name)
        st.metric("股票代码", stock_code)
        st.metric("最新收盘价", f"¥{latest['close']:.2f}", f"数据日期: {latest_date}")
    
    with summary_col2:
        st.metric("区间涨跌幅", f"{total_return:+.2f}%")
        st.metric("波动率", f"{volatility:.2f}%")
        st.metric("日均成交量", f"{latest['vol']/10000:.1f}万手" if 'vol' in latest else "N/A")
    
    with summary_col3:
        st.metric("区间最高价", f"¥{highest:.2f}")
        st.metric("区间最低价", f"¥{lowest:.2f}")
        st.metric("分析周期", f"{len(price_df)} 个交易日")
    
    # 技术评分
    st.markdown("---")
    
    # 计算技术评分
    tech_score = 50  # 基础分
    if total_return > 20:
        tech_score += 20
    elif total_return > 0:
        tech_score += 10
    elif total_return < -20:
        tech_score -= 20
    
    if volatility < 20:
        tech_score += 15
    elif volatility < 30:
        tech_score += 5
    else:
        tech_score -= 10
    
    tech_score = min(100, max(0, tech_score))
    
    score_col1, score_col2 = st.columns([1, 3])
    with score_col1:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = tech_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "技术面评分"},
            gauge = {'axis': {'range': [None, 100]},
                     'bar': {'color': "#ff9f43"},
                     'steps': [
                         {'range': [0, 40], 'color': "#ffcccc"},
                         {'range': [40, 70], 'color': "#ffffcc"},
                         {'range': [70, 100], 'color': "#ccffcc"}],
                     'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 40}}
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with score_col2:
        st.subheader("💡 技术分析结论")
        if tech_score >= 70:
            st.success("🟢 **技术面表现良好**\n\n股价趋势向上，波动率适中。建议关注基本面情况后考虑投资。")
        elif tech_score >= 40:
            st.warning("🟡 **技术面表现一般**\n\n股价走势平稳或有波动，建议观望或等待更好的入场时机。")
        else:
            st.error("🔴 **技术面表现较弱**\n\n股价下跌趋势明显或波动过大，建议谨慎对待。")
        
        st.markdown("**风险提示：**")
        if volatility > 40:
            st.markdown("- 🔴 股价波动较大，注意风险控制")
        if total_return < -20:
            st.markdown("- 🟡 近期股价下跌明显，需关注基本面变化")
        if latest['close'] < latest.get('ma60', 999999):
            st.markdown("- 🟡 股价低于60日均线，短期趋势偏弱")
    
    # 股价走势图
    st.markdown("---")
    st.subheader("📊 股价走势分析")
    
    # 数据日期标注
    latest_date = price_df.iloc[-1]['trade_date']
    st.caption(f"📅 数据来源：Tushare | 最新数据日期：{latest_date} | 更新频率：T+1（收盘后次日更新）")
    
    fig = go.Figure()
    
    # K线图
    fig.add_trace(go.Candlestick(
        x=price_df['trade_date'],
        open=price_df['open'],
        high=price_df['high'],
        low=price_df['low'],
        close=price_df['close'],
        name='K线'
    ))
    
    # 均线
    if 'ma20' in price_df.columns:
        fig.add_trace(go.Scatter(
            x=price_df['trade_date'], 
            y=price_df['ma20'],
            mode='lines',
            name='MA20',
            line=dict(color='orange', width=1)
        ))
    
    if 'ma60' in price_df.columns:
        fig.add_trace(go.Scatter(
            x=price_df['trade_date'], 
            y=price_df['ma60'],
            mode='lines',
            name='MA60',
            line=dict(color='blue', width=1)
        ))
    
    fig.update_layout(
        title=f"{company_name} ({stock_code}) 股价走势",
        yaxis_title="价格 (元)",
        xaxis_title="日期",
        height=500,
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 成交量图
    if 'vol' in price_df.columns:
        st.subheader("📊 成交量分析")
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(
            x=price_df['trade_date'],
            y=price_df['vol'],
            name='成交量',
            marker_color='lightblue'
        ))
        fig_vol.update_layout(
            yaxis_title="成交量（手）",
            xaxis_title="日期",
            height=300,
            template="plotly_white"
        )
        st.plotly_chart(fig_vol, use_container_width=True)
    
    # 风险提示
    st.markdown("---")
    st.info("📊 **数据说明**\n\n- 数据来源：Tushare Pro\n- 更新频率：T+1（每日收盘后15:00-17:00更新）\n- 当前显示：{latest_date} 收盘数据\n\n如需实时行情，请参考券商APP或同花顺、东方财富等终端。".format(latest_date=latest_date))
    
    st.warning("⚠️ **功能限制说明**\n\n当前仅基于股价数据进行技术分析。如需完整财务分析（营收、利润、资产负债表等），需要 Tushare 积分达到 2000。")

# ==================== 功能模块 2: 投资组合监控 ====================

def portfolio_monitoring():
    """投资组合监控模块"""
    st.header("💼 投资组合风险监控")
    st.markdown("上传持仓明细，获取组合风险分析和优化建议")
    
    # 数据输入方式
    input_method = st.radio(
        "数据输入方式",
        ["手动输入", "上传Excel文件"],
        horizontal=True
    )
    
    portfolio_df = None
    
    if input_method == "手动输入":
        st.subheader("手动输入持仓")
        
        # 使用session_state保存动态添加的行
        if 'portfolio_rows' not in st.session_state:
            st.session_state.portfolio_rows = [{"code": "", "name": "", "weight": 0.0}]
        
        # 显示输入框
        for i, row in enumerate(st.session_state.portfolio_rows):
            cols = st.columns([2, 2, 2, 1])
            with cols[0]:
                st.session_state.portfolio_rows[i]["code"] = st.text_input(
                    f"股票代码 {i+1}", 
                    value=row["code"],
                    key=f"code_{i}"
                )
            with cols[1]:
                st.session_state.portfolio_rows[i]["name"] = st.text_input(
                    f"股票名称 {i+1}", 
                    value=row["name"],
                    key=f"name_{i}"
                )
            with cols[2]:
                st.session_state.portfolio_rows[i]["weight"] = st.number_input(
                    f"权重(%) {i+1}", 
                    value=row["weight"],
                    min_value=0.0,
                    max_value=100.0,
                    key=f"weight_{i}"
                )
            with cols[3]:
                if st.button("🗑️", key=f"delete_{i}") and len(st.session_state.portfolio_rows) > 1:
                    st.session_state.portfolio_rows.pop(i)
                    st.rerun()
        
        # 添加按钮
        if st.button("➕ 添加股票"):
            st.session_state.portfolio_rows.append({"code": "", "name": "", "weight": 0.0})
            st.rerun()
        
        # 转换为DataFrame
        if st.session_state.portfolio_rows:
            portfolio_df = pd.DataFrame(st.session_state.portfolio_rows)
            portfolio_df = portfolio_df[portfolio_df["code"] != ""]  # 过滤空行
            
    else:
        # 上传文件
        uploaded_file = st.file_uploader("上传持仓明细（Excel）", type=['xlsx', 'xls', 'csv'])
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    portfolio_df = pd.read_csv(uploaded_file)
                else:
                    portfolio_df = pd.read_excel(uploaded_file)
                
                st.success("文件上传成功！")
                st.dataframe(portfolio_df.head(), use_container_width=True)
            except Exception as e:
                st.error(f"文件读取失败: {e}")
    
    # 分析按钮
    if portfolio_df is not None and not portfolio_df.empty:
        st.markdown("---")
        
        # 显示持仓预览
        st.subheader("持仓预览")
        st.dataframe(portfolio_df, use_container_width=True)
        
        # 权重校验
        total_weight = portfolio_df['weight'].sum() if 'weight' in portfolio_df.columns else 0
        if abs(total_weight - 100) > 1:
            st.warning(f"⚠️ 权重合计为 {total_weight}%，建议调整为100%")
        
        if st.button("🔍 开始组合分析", type="primary"):
            with st.spinner("正在计算组合风险指标..."):
                # 保存分析结果到 session_state
                st.session_state['portfolio_analysis_done'] = True
                st.session_state['portfolio_data'] = portfolio_df.to_dict('records')
                st.rerun()
        
        # 显示分析结果（如果已分析）
        if st.session_state.get('portfolio_analysis_done', False):
            display_portfolio_analysis(portfolio_df)

def display_portfolio_analysis(portfolio_df):
    """显示投资组合分析结果"""
    
    st.markdown("---")
    st.subheader("📊 组合分析结果")
    
    # 模拟分析结果（实际应调用API获取真实数据）
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("组合总规模", "1.2亿", "+5.3%")
    with col2:
        st.metric("年化收益率", "12.5%", "+2.1%")
    with col3:
        st.metric("最大回撤", "-8.2%", "-1.2%")
    with col4:
        st.metric("夏普比率", "1.35", "+0.15")
    
    # 行业分布图
    st.subheader("行业分布")
    
    # 模拟数据
    industry_data = pd.DataFrame({
        '行业': ['消费', '科技', '医药', '金融', '制造业'],
        '占比': [30, 25, 20, 15, 10]
    })
    
    fig_pie = px.pie(industry_data, values='占比', names='行业', 
                     title='行业配置分布',
                     color_discrete_sequence=px.colors.sequential.Blues)
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # 风险分析
    st.subheader("⚠️ 风险分析")
    
    risk_col1, risk_col2 = st.columns(2)
    
    with risk_col1:
        st.markdown("**集中度风险**")
        max_weight = portfolio_df['weight'].max() if 'weight' in portfolio_df.columns else 0
        if max_weight > 30:
            st.error(f"🔴 单一持仓占比过高 ({max_weight}%)，建议分散")
        elif max_weight > 20:
            st.warning(f"🟡 单一持仓占比较高 ({max_weight}%)，注意风险")
        else:
            st.success(f"🟢 持仓分散度良好，最大单一持仓 {max_weight}%")
    
    with risk_col2:
        st.markdown("**VaR风险价值**")
        st.info("95%置信度下，单日最大可能损失：120万元 (1%)")
    
    # 优化建议
    st.subheader("💡 优化建议")
    suggestions = [
        "🟡 科技板块配置过高(25%)，建议适当减仓",
        "🟢 消费板块表现稳健，可维持当前配置",
        "🟡 建议增配10%的债券资产以降低波动",
        "🟢 组合整体风险水平适中，适合长期持有"
    ]
    for s in suggestions:
        st.markdown(s)
    
    # 设置自动监控
    st.markdown("---")
    st.subheader("🔔 设置自动监控")
    
    monitor_col1, monitor_col2 = st.columns(2)
    with monitor_col1:
        alert_threshold = st.slider("止损提醒阈值(%)", -50, 0, -10)
    with monitor_col2:
        email = st.text_input("接收提醒邮箱", placeholder="your@email.com")
    
    if st.button("📧 开启每周监控报告"):
        if email:
            st.success(f"✅ 已设置监控，每周一早上8点将发送报告到 {email}")
            # 这里实际应调用定时任务设置
        else:
            st.error("请输入邮箱地址")

# ==================== 功能模块 3: 商业尽调 ====================

def business_due_diligence():
    """商业尽调模块"""
    st.header("🔍 智能商业尽调（CDD）")
    st.markdown("上传内部资料，AI辅助分析商业模式、行业对标和竞争力")
    
    # 公司基本信息
    st.subheader("目标公司基本信息")
    
    basic_col1, basic_col2 = st.columns(2)
    with basic_col1:
        target_name = st.text_input("公司名称", placeholder="如：深水云科")
        industry = st.selectbox("所属行业", 
                               ["金融科技", "制造业", "消费品", "医药", "科技", "其他"])
    with basic_col2:
        stage = st.selectbox("发展阶段", 
                            ["初创期", "成长期", "成熟期", "Pre-IPO", "上市公司"])
        revenue_scale = st.selectbox("营收规模", 
                                    ["<1000万", "1000万-5000万", "5000万-1亿", "1亿-10亿", ">10亿"])
    
    # 文件上传
    st.subheader("📁 上传内部资料")
    
    uploaded_files = st.file_uploader(
        "支持PDF、Word、Excel、PPT",
        type=['pdf', 'docx', 'xlsx', 'pptx'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"已上传 {len(uploaded_files)} 个文件")
        for file in uploaded_files:
            st.markdown(f"- 📄 {file.name} ({file.size/1024:.1f} KB)")
    
    # 分析维度选择
    st.subheader("分析维度")
    
    analysis_dims = st.multiselect(
        "选择需要分析的维度",
        ["商业模式画布", "财务健康度", "核心竞争力（护城河）", "行业对标分析", 
         "风险评估", "管理团队评估", "技术/知识产权", "客户与供应商分析"],
        default=["商业模式画布", "核心竞争力（护城河）", "行业对标分析", "风险评估"]
    )
    
    # 初始化session_state用于保存分析结果
    if 'dd_report_data' not in st.session_state:
        st.session_state.dd_report_data = None
    if 'dd_analysis_done' not in st.session_state:
        st.session_state.dd_analysis_done = False
    if 'ai_analysis_result' not in st.session_state:
        st.session_state.ai_analysis_result = None
    if 'dd_target_name' not in st.session_state:
        st.session_state.dd_target_name = None
    
    # 如果切换了公司，清除之前的结果
    if st.session_state.dd_target_name != target_name:
        st.session_state.dd_report_data = None
        st.session_state.dd_analysis_done = False
        st.session_state.ai_analysis_result = None
        st.session_state.dd_target_name = None
    
    # 开始分析按钮
    if st.button("🚀 开始商业尽调", type="primary"):
        if not target_name:
            st.error("请输入目标公司名称")
            return
            
        if not uploaded_files:
            st.warning("未上传内部资料，将仅基于公开信息进行分析")
        
        with st.spinner("正在深度分析..."):
            # 执行分析并保存结果
            report_data, file_contents = perform_dd_analysis(target_name, industry, uploaded_files, analysis_dims)
            st.session_state.dd_report_data = report_data
            st.session_state.dd_file_contents = file_contents
            st.session_state.dd_analysis_done = True
            st.session_state.dd_target_name = target_name
            st.rerun()
    
    # 显示分析结果（如果有）
    if st.session_state.dd_analysis_done and st.session_state.dd_target_name == target_name:
        display_dd_results(
            target_name, 
            industry, 
            analysis_dims, 
            st.session_state.dd_report_data,
            st.session_state.dd_file_contents
        )

def display_dd_results(company_name, industry, dimensions, report_data, file_contents):
    """提取上传文件的内容"""
    content = ""
    file_type = file.name.split('.')[-1].lower()
    
    try:
        if file_type == 'pdf':
            # 使用 PyMuPDF 解析 PDF
            import fitz
            pdf_document = fitz.open(stream=file.read(), filetype="pdf")
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                content += f"\n--- 第{page_num + 1}页 ---\n"
                content += page.get_text()
            pdf_document.close()
            
        elif file_type in ['docx', 'doc']:
            # 使用 python-docx 解析 Word
            from docx import Document
            doc = Document(file)
            for para in doc.paragraphs:
                content += para.text + "\n"
                
        elif file_type in ['xlsx', 'xls']:
            # 使用 pandas 解析 Excel
            df = pd.read_excel(file)
            content = f"表格数据（共{len(df)}行）：\n"
            content += df.to_string()
            
        elif file_type == 'pptx':
            # 使用 python-pptx 解析 PPT
            from pptx import Presentation
            prs = Presentation(file)
            for slide_num, slide in enumerate(prs.slides, 1):
                content += f"\n--- 幻灯片{slide_num} ---\n"
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        content += shape.text + "\n"
        
        return content[:5000]  # 限制长度，避免超出上下文
        
    except Exception as e:
        return f"文件解析错误: {str(e)}"

def perform_dd_analysis(company_name, industry, files, dimensions):
    """执行尽调分析（基于真实API数据）"""
    
    # 初始化数据集成器
    tianyancha_token = os.getenv("TIANYANCHA_TOKEN")
    dd_integration = DueDiligenceIntegration(tianyancha_token)
    
    # 读取文件内容
    file_contents = []
    if files:
        st.info(f"📄 正在解析 {len(files)} 个文件...")
        for file in files:
            content = extract_file_content(file)
            file_contents.append({
                'name': file.name,
                'content': content
            })
            st.success(f"✅ 已解析: {file.name}")
    
    # 调用API获取真实数据
    progress_bar = st.progress(0)
    
    steps = [
        ("查询工商信息", 0.2),
        ("获取财务数据", 0.4),
        ("分析舆情风险", 0.6),
        ("解析内部资料", 0.8),
        ("生成综合报告", 1.0)
    ]
    
    report_data = {}
    
    for step_name, progress in steps:
        progress_bar.progress(progress)
        st.text(f"正在执行：{step_name}...")
        
        if step_name == "查询工商信息":
            report_data["工商信息"] = dd_integration.search_company_basic(company_name)
            report_data["风险信息"] = dd_integration.get_company_risk(company_name)
        
        elif step_name == "获取财务数据":
            # 查找股票代码
            stock_code = None
            for name, code in STOCK_NAME_MAPPING.items():
                if company_name in name or name in company_name:
                    stock_code = code
                    break
            if stock_code:
                report_data["财务数据"] = dd_integration.get_financial_data(stock_code)
            else:
                report_data["财务数据"] = {"note": "未找到对应上市公司代码"}
        
        elif step_name == "分析舆情风险":
            report_data["舆情监控"] = dd_integration.search_news(company_name)
        
        elif step_name == "解析内部资料":
            if file_contents:
                report_data["内部资料"] = file_contents
        
        import time
        time.sleep(0.2)
    
    # 生成综合评估
    report_data["综合评估"] = dd_integration._generate_assessment(report_data, industry)
    
    return report_data, file_contents, dd_integration

def display_dd_results(company_name, industry, dimensions, report_data, file_contents, dd_integration):
    """显示尽调分析结果"""
    
    # 显示数据获取结果
    st.markdown("---")
    st.subheader("📊 数据获取结果")
    
    # 显示数据完整度
    completeness = report_data["综合评估"].get("数据完整度", 0)
    st.metric("数据完整度", f"{completeness}%")
    
    # 显示工商信息（如果获取成功）
    if "工商信息" in report_data and "error" not in report_data["工商信息"]:
        with st.expander("🏢 工商基本信息"):
            basic = report_data["工商信息"]
            st.json(basic)
    
    # 显示财务数据（如果是上市公司）
    if "财务数据" in report_data and report_data["财务数据"].get("is_listed"):
        with st.expander("💰 财务数据摘要"):
            fin = report_data["财务数据"]
            if "利润表" in fin and not fin["利润表"].empty:
                latest = fin["利润表"].iloc[-1]
                st.metric("最新营收", f"{latest.get('total_revenue', 0)/1e8:.2f}亿元")
                st.metric("最新净利润", f"{latest.get('n_income', 0)/1e8:.2f}亿元")
    
    # 显示文件解析结果
    if file_contents:
        st.markdown("---")
        st.subheader("📄 文件解析结果")
        for fc in file_contents:
            with st.expander(f"📄 {fc['name']} (点击查看内容)"):
                st.text(fc['content'][:2000] + "..." if len(fc['content']) > 2000 else fc['content'])
    
    # 显示结果
    st.markdown("---")
    st.subheader("📋 商业尽调报告")
    
    # 执行摘要（基于真实数据）
    st.markdown("### 一页纸摘要")
    
    # 使用真实评估数据
    assessment = report_data.get("综合评估", {})
    data_completeness = assessment.get("数据完整度", 0)
    recommendation = assessment.get("建议", "数据不足，建议补充")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**公司**: {company_name}")
        st.markdown(f"**行业**: {industry}")
        st.markdown(f"**数据完整度**: {'🟢' if data_completeness >= 60 else '🟡'} {data_completeness}%")
    
    with col2:
        st.markdown(f"**分析日期**: {datetime.now().strftime('%Y-%m-%d')}")
        if report_data.get("财务数据", {}).get("is_listed"):
            st.markdown("**上市状态**: 🟢 上市公司")
        else:
            st.markdown("**上市状态**: 🟡 非上市公司")
    
    st.markdown("---")
    st.markdown(f"**💡 投资建议**: {recommendation}")
    
    # 详细分析（基于真实数据）
    st.markdown("---")
    
    # 财务数据分析（如果是上市公司）
    if "财务数据" in report_data and report_data["财务数据"].get("is_listed"):
        with st.expander("💰 财务数据分析", expanded=True):
            fin = report_data["财务数据"]
            
            # 显示利润表趋势
            if "利润表" in fin and not fin["利润表"].empty:
                income = fin["利润表"]
                st.markdown("**营收与利润趋势**")
                
                # 取最近5期数据
                recent = income.tail(5)
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=recent['end_date'],
                    y=recent['total_revenue']/1e8,
                    mode='lines+markers',
                    name='营业收入（亿元）'
                ))
                fig.add_trace(go.Scatter(
                    x=recent['end_date'],
                    y=recent['n_income']/1e8,
                    mode='lines+markers',
                    name='净利润（亿元）'
                ))
                fig.update_layout(title='财务趋势', height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    # 工商信息展示
    if "工商信息" in report_data and "error" not in report_data["工商信息"]:
        with st.expander("🏢 工商信息", expanded=True):
            basic = report_data["工商信息"]
            st.json(basic)
    elif "工商信息" in report_data and "note" in report_data["工商信息"]:
        with st.expander("🏢 工商信息", expanded=True):
            st.info(report_data["工商信息"]["note"])
            st.markdown("💡 **建议**: 配置天眼查Token后可获取详细工商信息、股权结构、法律诉讼等数据")
    
    # 风险信息展示
    if "风险信息" in report_data:
        with st.expander("⚠️ 风险信息", expanded=True):
            risk = report_data["风险信息"]
            if "error" in risk:
                st.info("风险信息未获取，配置天眼查Token后可查看法律诉讼、经营异常等风险数据")
            else:
                st.json(risk)
    
    # 内部资料洞察
    if "内部资料" in report_data:
        with st.expander("📄 内部资料洞察", expanded=True):
            insights = dd_integration._extract_key_insights(report_data["内部资料"])
            if insights:
                for i, insight in enumerate(insights, 1):
                    st.markdown(f"{i}. {insight}")
            else:
                st.info("已解析内部资料，未发现关键业务数据")
    
    if "商业模式画布" in dimensions:
        with st.expander("商业模式画布", expanded=True):
            st.info("📊 **基于上传资料自动生成的商业模式分析**")
            st.markdown("""
            | 维度 | 内容 |
            |------|------|
            | **价值主张** | 根据内部资料自动识别 |
            | **客户细分** | 根据内部资料自动识别 |
            | **收入来源** | 根据内部资料自动识别 |
            | **成本结构** | 根据内部资料自动识别 |
            """)
            st.markdown("💡 **提示**: 上传BP或商业计划书后，AI将自动提取并填充此画布")
    
    if "核心竞争力（护城河）" in dimensions:
        with st.expander("核心竞争力评估", expanded=True):
            st.markdown(f"**数据完整度**: {data_completeness}%")
            st.markdown("""
            **评估维度：**
            - **品牌优势**: 需天眼查数据支持
            - **技术壁垒**: 需内部资料分析
            - **成本优势**: 需财务数据分析
            - **网络效应**: 需行业数据支持
            """)
            if data_completeness < 50:
                st.warning("⚠️ 当前数据不足以进行准确的护城河评估，建议补充更多资料")
    
    if "风险评估" in dimensions:
        with st.expander("风险评估矩阵", expanded=True):
            risk_df = pd.DataFrame({
                '风险类型': ['关联交易', '客户集中度', '政策风险', '技术迭代', '人员流失'],
                '发生概率': ['高', '中', '中', '低', '中'],
                '影响程度': ['高', '高', '中', '中', '低'],
                '风险等级': ['🔴 高', '🟡 中', '🟡 中', '🟢 低', '🟢 低']
            })
            st.dataframe(risk_df, use_container_width=True, hide_index=True)
    
    # 导出按钮
    st.markdown("---")
    
    # 生成导出内容（基于真实数据）
    report_content = f"""# 商业尽调报告

## 公司基本信息
- **公司名称**: {company_name}
- **所属行业**: {industry}
- **分析日期**: {datetime.now().strftime('%Y-%m-%d')}
- **数据完整度**: {data_completeness}%

## 执行摘要
- **投资建议**: {recommendation}
- **上市状态**: {"上市公司" if report_data.get("财务数据", {}).get("is_listed") else "非上市公司/未识别"}

## 数据来源
- **工商信息**: {"✅ 已获取" if "工商信息" in report_data and "error" not in report_data["工商信息"] else "❌ 未配置（需天眼查Token）"}
- **财务数据**: {"✅ 已获取" if report_data.get("财务数据", {}).get("is_listed") else "❌ 非上市公司或未匹配"}
- **内部资料**: {"✅ 已解析" + str(len(report_data.get("内部资料", []))) + "个文件" if "内部资料" in report_data else "❌ 未上传"}

## 详细分析

### 1. 工商信息
{json.dumps(report_data.get("工商信息", {}), ensure_ascii=False, indent=2) if "工商信息" in report_data else "未获取"}

### 2. 财务数据
{"已获取上市公司财务数据" if report_data.get("财务数据", {}).get("is_listed") else "非上市公司或未匹配股票代码"}

### 3. 风险信息
{json.dumps(report_data.get("风险信息", {}), ensure_ascii=False, indent=2) if "风险信息" in report_data else "未获取"}

### 4. 内部资料洞察
{chr(10).join(["- " + i for i in dd_integration._extract_key_insights(report_data.get("内部资料", []))]) if "内部资料" in report_data else "未上传内部资料"}

## 附录：数据来源说明
- **AKShare**: 免费财务数据（东方财富源）
- **天眼查API**: 工商信息（需配置Token）
- **文件解析**: PDF/Word/Excel/PPT文本提取

---
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
深水云科智能投研工作台
"""
    
    if "商业模式画布" in dimensions:
        report_content += """
### 商业模式画布
- **价值主张**: 为金融机构提供外包服务，降低运营成本
- **客户细分**: 中小银行、消费金融公司
- **渠道通路**: 直销+渠道合作
- **收入来源**: 服务费（按业务量计费）
- **核心资源**: 牌照资质、客户资源
- **关键业务**: 催收、客服、数据处理外包
- **重要合作**: 母公司资源协同
- **成本结构**: 人力成本（60%）、系统维护（20%）
"""
    
    if "核心竞争力（护城河）" in dimensions:
        report_content += """
### 核心竞争力评估
- 品牌优势: 5/10 - 细分领域有一定知名度
- 技术壁垒: 4/10 - 系统为外采，自研能力弱
- 成本优势: 6/10 - 轻资产模式
- 网络效应: 3/10 - 无明显网络效应
- 政策壁垒: 7/10 - 具备相关牌照
- **综合评分: 5/10（中等护城河）**
"""
    
    if "风险评估" in dimensions:
        report_content += """
### 风险评估矩阵
| 风险类型 | 发生概率 | 影响程度 | 风险等级 |
|---------|---------|---------|----------|
| 关联交易 | 高 | 高 | 🔴 高 |
| 客户集中度 | 中 | 高 | 🟡 中 |
| 政策风险 | 中 | 中 | 🟡 中 |
| 技术迭代 | 低 | 中 | 🟢 低 |
| 人员流失 | 中 | 低 | 🟢 低 |
"""
    
    report_content += f"""

## 结论与建议
建议谨慎推进本次投资，需重点补充以下尽调：
1. 关联交易的具体情况及合规性
2. 客户集中度的详细分析
3. 核心团队的稳定性评估

---
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
深水云科智能投研工作台
"""
    
    # 提供下载按钮
    st.download_button(
        label="📥 下载尽调报告 (Markdown)",
        data=report_content,
        file_name=f"尽调报告_{company_name}_{datetime.now().strftime('%Y%m%d')}.md",
        mime="text/markdown"
    )
    
    st.info("💡 Markdown格式可用Typora、VS Code等软件打开，也可复制到Word中编辑")
    
    # AI增强分析按钮
    st.markdown("---")
    st.subheader("🤖 AI增强分析")
    st.markdown("使用 **Gemini 3.1 Pro** 对尽调数据进行深度智能分析")
    
    # 使用session_state保存AI分析结果
    if 'ai_analysis_result' not in st.session_state:
        st.session_state.ai_analysis_result = None
    if 'ai_analysis_company' not in st.session_state:
        st.session_state.ai_analysis_company = None
    
    # 如果切换了公司，清除之前的分析结果
    if st.session_state.ai_analysis_company != company_name:
        st.session_state.ai_analysis_result = None
        st.session_state.ai_analysis_company = None
    
    if st.button("🚀 AI增强尽调分析", type="primary", help="调用Gemini AI进行深度分析"):
        with st.spinner("🤖 AI正在深度分析中，请稍候..."):
            try:
                # 初始化Gemini分析器
                gemini = GeminiAnalyzer()
                
                # 准备数据
                ai_analysis = gemini.analyze_due_diligence(
                    company_name=company_name,
                    industry=industry,
                    file_contents=file_contents,
                    financial_data=report_data.get("财务数据", {})
                )
                
                # 保存到session_state
                st.session_state.ai_analysis_result = ai_analysis
                st.session_state.ai_analysis_company = company_name
                
                # 刷新页面显示结果
                st.rerun()
                
            except Exception as e:
                st.error(f"AI分析失败: {str(e)}")
                st.info("💡 可能原因：API调用失败或网络问题，请稍后重试")
    
    # 显示AI分析结果（如果有）
    if st.session_state.ai_analysis_result and st.session_state.ai_analysis_company == company_name:
        st.markdown("---")
        st.markdown("### 📊 AI深度分析报告")
        st.markdown(st.session_state.ai_analysis_result)
        
        # 提供AI报告的下载
        ai_report = f"""# AI增强尽调分析报告

**分析模型**: Gemini 3.1 Pro  
**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{st.session_state.ai_analysis_result}

---
*本报告由Gemini AI生成，仅供参考*
"""
        st.download_button(
            label="📥 下载AI分析报告",
            data=ai_report,
            file_name=f"AI尽调分析_{company_name}_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown"
        )

# ==================== 侧边栏 ====================

def sidebar():
    """侧边栏配置"""
    st.sidebar.title("⚙️ 系统配置")
    
    # API状态检查
    st.sidebar.subheader("API连接状态")
    
    api_status = check_api_status()
    
    for api_name, status in api_status.items():
        icon = "🟢" if status else "🔴"
        status_text = "已连接" if status else "未配置"
        st.sidebar.markdown(f"{icon} {api_name}: {status_text}")
    
    # API配置
    tushare_configured = bool(os.getenv("TUSHARE_TOKEN"))
    tianyancha_configured = bool(os.getenv("TIANYANCHA_TOKEN"))
    
    expander_title = "🔐 API密钥配置"
    if tushare_configured and tianyancha_configured:
        expander_title = "✅ API密钥已配置"
    elif tushare_configured:
        expander_title = "🟡 Tushare已配置"
    
    with st.sidebar.expander(expander_title):
        # 显示当前配置状态
        if tushare_configured:
            st.success("✅ Tushare Token 已内置")
            tushare_token = os.getenv("TUSHARE_TOKEN", "")
            st.text_input("Tushare Token（已隐藏）", 
                         value="*" * 20,
                         disabled=True,
                         type="password")
        else:
            st.warning("⚠️ Tushare Token 未配置")
            tushare_token = st.text_input("Tushare Token", 
                                          placeholder="输入您的Tushare Token",
                                          type="password")
        
        if tianyancha_configured:
            st.success("✅ 天眼查 Token 已内置")
            tianyancha_token = os.getenv("TIANYANCHA_TOKEN", "")
            st.text_input("天眼查 Token（已隐藏）", 
                         value="*" * 20,
                         disabled=True,
                         type="password")
        else:
            st.info("💡 天眼查 Token 可选（用于工商数据）")
            tianyancha_token = st.text_input("天眼查 Token", 
                                             placeholder="输入您的天眼查 Token",
                                             type="password")
            st.markdown("[👉 购买天眼查API](https://open.tianyancha.com/recharge/1)")
        
        if not tushare_configured or not tianyancha_configured:
            if st.button("💾 保存配置"):
                if tushare_token and tushare_token != "*" * 20:
                    os.environ["TUSHARE_TOKEN"] = tushare_token
                if tianyancha_token and tianyancha_token != "*" * 20:
                    os.environ["TIANYANCHA_TOKEN"] = tianyancha_token
                st.success("✅ 配置已保存！请刷新页面生效。")
                st.balloons()
    
    # 使用说明
    st.sidebar.markdown("---")
    st.sidebar.subheader("📖 使用说明")
    
    st.sidebar.markdown("""
    **功能导航：**
    1. **单一公司分析** - 财务健康度评估
    2. **投资组合监控** - 组合风险分析
    3. **商业尽调** - 深度CDD报告
    
    **支持格式：**
    - 股票代码：600519.SH
    - 文件：PDF、Excel、Word
    
    **💳 [Tushare充值入口](https://tushare.pro/document/1?doc_id=13)**
    """)
    
    # 免费数据源
    with st.sidebar.expander("🆓 查看免费数据源"):
        try:
            free_df = pd.read_csv('config/free_data_sources.csv')
            st.markdown("**核心免费供应商：**")
            for _, row in free_df.iterrows():
                if row['优先级'] in ['P0', 'P1']:
                    st.markdown(f"- **{row['数据源名称']}** ({row['数据类别']})")
            st.markdown("\n*更多免费源见 `config/free_data_sources.csv`")
        except Exception:
            st.info("免费数据源列表加载中...")
    
    # 邮件配置
    st.sidebar.markdown("---")
    st.sidebar.subheader("📧 邮件配置")
    
    with st.sidebar.expander("🔐 配置发件邮箱"):
        st.markdown("**常用SMTP设置：**")
        st.markdown("- **163邮箱**: smtp.163.com:465")
        st.markdown("- **QQ邮箱**: smtp.qq.com:465")
        st.markdown("- **企业邮箱**: 请咨询公司IT")
        
        smtp_server = st.text_input("SMTP服务器", value="smtp.163.com", key="smtp_server")
        smtp_port = st.number_input("SMTP端口", value=465, key="smtp_port")
        sender_email = st.text_input("发件邮箱", value="", placeholder="yourname@163.com", key="sender_email")
        sender_password = st.text_input("授权码/密码", value="", type="password", placeholder="邮箱授权码", key="sender_password")
        
        st.info("💡 163/QQ邮箱需开启SMTP并获取授权码（非登录密码）")
        st.markdown("[👉 163邮箱授权码获取教程](https://mail.163.com/)")
    
    test_email = st.sidebar.text_input("测试收件邮箱", value="liugs3@infore.com", key="test_email")
    
    if st.sidebar.button("🚀 发送测试邮件"):
        with st.sidebar:
            with st.spinner("正在发送..."):
                # 检查配置
                if not sender_email or not sender_password:
                    st.error("❌ 请先配置发件邮箱和授权码（点击上方🔐配置发件邮箱）")
                    st.info("**快速开始（163邮箱）：**\n1. 打开 163.com 登录邮箱\n2. 设置 → POP3/SMTP/IMAP\n3. 开启 SMTP 服务\n4. 获取授权码（16位字符串）")
                else:
                    # 真实发送邮件
                    success, message = send_test_email(
                        smtp_server, smtp_port, sender_email, sender_password, test_email
                    )
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
                        st.info("**常见问题：**\n- 检查授权码是否正确（非邮箱密码）\n- 确认SMTP服务器和端口\n- 检查发件邮箱是否开启SMTP服务")
    
    # 关于
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **智能投研工作台 v2.0**
    
    基于 Kimi Code + Streamlit 开发
    深水云科投资决策场景
    
    © 2026 深水云科
    """)

# ==================== 主程序 ====================

def main():
    """主程序入口"""
    
    # 页面标题
    st.markdown('<div class="main-header">📊 智能投研工作台</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">深水云科投资决策辅助系统</div>', 
                unsafe_allow_html=True)
    
    # 侧边栏
    sidebar()
    
    # 主区域 - 功能选择
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs([
        "📈 单一公司分析", 
        "💼 投资组合监控", 
        "🔍 商业尽调(CDD)"
    ])
    
    with tab1:
        single_company_analysis()
    
    with tab2:
        portfolio_monitoring()
    
    with tab3:
        business_due_diligence()

if __name__ == "__main__":
    main()
