#!/usr/bin/env python3
"""
金融Agent模块
封装原有的三大场景，提供对话式交互
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apis.akshare_api import AKShareFinanceAPI
from apis.gemini_api import GeminiAnalyzer

def company_analysis_mode():
    """公司财务分析模式"""
    
    st.markdown("### 📈 公司财务深度分析")
    st.markdown("输入股票代码或公司名称，获取全面的财务健康度评估")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        input_type = st.radio("输入方式", ["股票代码", "公司名称"], horizontal=True)
        
        if input_type == "股票代码":
            stock_code = st.text_input("股票代码", placeholder="600519.SH", 
                                     help="格式：代码.交易所（SH=上海，SZ=深圳）")
        else:
            company_name = st.text_input("公司名称", placeholder="贵州茅台")
            stock_code = None
    
    with col2:
        st.markdown("**分析选项**")
        data_source = st.radio("数据源", ["AKShare（免费）"], index=0)
        analysis_period = st.selectbox("周期", ["近3年", "近5年", "近10年"], index=1)
        include_risk = st.checkbox("风险排雷", value=True)
    
    # 分析按钮
    if st.button("🚀 开始分析", type="primary", use_container_width=True):
        if not stock_code and input_type == "股票代码":
            st.warning("请输入股票代码")
            return
        
        with st.spinner("正在获取数据并分析..."):
            try:
                # 初始化API
                ak_api = AKShareFinanceAPI()
                
                # 获取数据
                if input_type == "公司名称":
                    # 通过名称查找代码（简化版）
                    stock_code = find_stock_code(company_name)
                    if not stock_code:
                        st.error("未找到对应股票代码")
                        return
                
                # 获取财务数据
                income_df = ak_api.get_income_statement(stock_code)
                
                if income_df.empty:
                    st.error("未获取到财务数据")
                    return
                
                # 显示结果
                display_financial_results(income_df, stock_code)
                
            except Exception as e:
                st.error(f"分析失败: {str(e)}")

def find_stock_code(company_name: str) -> str:
    """通过公司名称查找股票代码"""
    # 常用映射表
    mapping = {
        "茅台": "600519.SH",
        "贵州茅台": "600519.SH",
        "腾讯": "00700.HK",
        "阿里巴巴": "BABA",
        "平安": "601318.SH",
        "招商银行": "600036.SH"
    }
    return mapping.get(company_name)

def display_financial_results(income_df: pd.DataFrame, stock_code: str):
    """显示财务分析结果"""
    
    st.success(f"✅ 成功获取 {stock_code} 财务数据")
    
    # 计算指标
    latest = income_df.iloc[-1]
    previous = income_df.iloc[-2] if len(income_df) > 1 else latest
    
    # 计算增长率
    revenue_growth = (latest['total_revenue'] - previous['total_revenue']) / previous['total_revenue'] * 100 if previous['total_revenue'] != 0 else 0
    profit_growth = (latest['n_income'] - previous['n_income']) / previous['n_income'] * 100 if previous['n_income'] != 0 else 0
    
    # KPI卡片
    st.markdown("#### 📊 关键指标")
    kpi_cols = st.columns(4)
    
    with kpi_cols[0]:
        st.metric("最新营收", f"{latest['total_revenue']/1e8:.1f}亿", f"{revenue_growth:.1f}%")
    with kpi_cols[1]:
        st.metric("最新净利润", f"{latest['n_income']/1e8:.1f}亿", f"{profit_growth:.1f}%")
    with kpi_cols[2]:
        margin = latest['n_income'] / latest['total_revenue'] * 100 if latest['total_revenue'] != 0 else 0
        st.metric("净利率", f"{margin:.1f}%")
    with kpi_cols[3]:
        health_score = calculate_health_score(revenue_growth, profit_growth, margin)
        st.metric("健康度评分", f"{health_score}/100")
    
    # 趋势图
    st.markdown("#### 📈 营收趋势")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=income_df['end_date'],
        y=income_df['total_revenue'] / 1e8,
        mode='lines+markers',
        name='营业收入（亿元）'
    ))
    fig.add_trace(go.Scatter(
        x=income_df['end_date'],
        y=income_df['n_income'] / 1e8,
        mode='lines+markers',
        name='净利润（亿元）'
    ))
    fig.update_layout(height=400, xaxis_title='报告期', yaxis_title='金额（亿元）')
    st.plotly_chart(fig, use_container_width=True)
    
    # 数据表
    with st.expander("查看原始数据"):
        st.dataframe(income_df, use_container_width=True)

def calculate_health_score(revenue_growth, profit_growth, margin):
    """计算健康度评分"""
    score = 50
    if revenue_growth > 20:
        score += 15
    elif revenue_growth > 10:
        score += 10
    elif revenue_growth > 0:
        score += 5
    
    if profit_growth > 20:
        score += 15
    elif profit_growth > 10:
        score += 10
    elif profit_growth > 0:
        score += 5
    
    if margin > 20:
        score += 10
    elif margin > 10:
        score += 5
    
    return min(100, score)

def portfolio_monitor_mode():
    """投资组合监控模式"""
    
    st.markdown("### 📊 投资组合监控")
    st.markdown("监控多资产组合表现，分析风险与收益")
    
    # 示例数据
    st.info("💡 提示：可以上传持仓CSV文件，或使用下方示例数据体验功能")
    
    use_example = st.checkbox("使用示例数据", value=True)
    
    if use_example:
        # 示例持仓
        portfolio_data = {
            'stock_code': ['600519.SH', '601318.SH', '600036.SH', '000858.SZ', '002415.SZ'],
            'stock_name': ['贵州茅台', '中国平安', '招商银行', '五粮液', '海康威视'],
            'quantity': [100, 500, 1000, 200, 300],
            'avg_price': [1500, 45, 35, 150, 30],
            'current_price': [1680, 48, 38, 165, 32]
        }
        portfolio_df = pd.DataFrame(portfolio_data)
        portfolio_df['market_value'] = portfolio_df['quantity'] * portfolio_df['current_price']
        portfolio_df['cost'] = portfolio_df['quantity'] * portfolio_df['avg_price']
        portfolio_df['profit'] = portfolio_df['market_value'] - portfolio_df['cost']
        portfolio_df['return_pct'] = portfolio_df['profit'] / portfolio_df['cost'] * 100
        
        display_portfolio_analysis(portfolio_df)
    else:
        uploaded = st.file_uploader("上传持仓CSV", type=['csv'])
        if uploaded:
            portfolio_df = pd.read_csv(uploaded)
            display_portfolio_analysis(portfolio_df)

def display_portfolio_analysis(portfolio_df: pd.DataFrame):
    """显示组合分析结果"""
    
    total_value = portfolio_df['market_value'].sum()
    total_cost = portfolio_df['cost'].sum()
    total_profit = total_value - total_cost
    total_return = total_profit / total_cost * 100
    
    # 总览
    st.markdown("#### 💰 组合总览")
    cols = st.columns(4)
    with cols[0]:
        st.metric("总市值", f"¥{total_value/1e4:.1f}万")
    with cols[1]:
        st.metric("总成本", f"¥{total_cost/1e4:.1f}万")
    with cols[2]:
        st.metric("总盈亏", f"¥{total_profit/1e4:.1f}万", f"{total_return:.1f}%")
    with cols[3]:
        st.metric("持仓数量", f"{len(portfolio_df)}只")
    
    # 持仓分布
    st.markdown("#### 📊 持仓分布")
    portfolio_df['weight'] = portfolio_df['market_value'] / total_value * 100
    
    fig = px.pie(portfolio_df, values='market_value', names='stock_name', 
                 title='市值分布', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
    
    # 明细表
    st.markdown("#### 📋 持仓明细")
    st.dataframe(portfolio_df[['stock_name', 'quantity', 'avg_price', 'current_price', 
                               'market_value', 'profit', 'return_pct', 'weight']], 
                use_container_width=True)
    
    # 风险提醒
    st.markdown("#### ⚠️ 风险分析")
    max_weight = portfolio_df['weight'].max()
    if max_weight > 30:
        st.error(f"🔴 集中度风险：单只股票占比过高（{max_weight:.1f}%）")
    elif max_weight > 20:
        st.warning(f"🟡 集中度风险：单只股票占比较高（{max_weight:.1f}%）")
    else:
        st.success(f"🟢 持仓分散度良好，最大单一持仓 {max_weight:.1f}%")

def due_diligence_mode():
    """商业尽调模式"""
    
    st.markdown("### 🔍 智能商业尽调（CDD）")
    st.markdown("上传尽调资料，AI辅助分析商业模式、行业对标和竞争力")
    
    # 公司信息
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("公司名称", placeholder="如：深水云科")
        industry = st.selectbox("所属行业", 
                               ["金融科技", "制造业", "消费品", "医药", "科技", "其他"])
    with col2:
        stage = st.selectbox("发展阶段", 
                            ["初创期", "成长期", "成熟期", "Pre-IPO", "上市公司"])
    
    # 文件上传
    st.markdown("#### 📁 上传尽调资料")
    uploaded_files = st.file_uploader(
        "支持PDF、Word、Excel、PPT",
        type=['pdf', 'docx', 'xlsx', 'pptx'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"已上传 {len(uploaded_files)} 个文件")
    
    # 分析维度
    analysis_dims = st.multiselect(
        "分析维度",
        ["商业模式画布", "财务健康度", "核心竞争力", "行业对标分析", 
         "风险评估", "管理团队评估", "技术/知识产权", "客户与供应商分析"],
        default=["商业模式画布", "核心竞争力", "行业对标分析", "风险评估"]
    )
    
    # 开始分析
    if st.button("🚀 开始商业尽调", type="primary", use_container_width=True):
        if not company_name:
            st.error("请输入公司名称")
            return
        
        with st.spinner("正在深度分析..."):
            # 模拟分析结果
            display_dd_results(company_name, industry, analysis_dims)

def display_dd_results(company_name: str, industry: str, dimensions: list):
    """显示尽调结果"""
    
    st.success(f"✅ 完成 {company_name} 商业尽调分析")
    
    # 执行摘要
    st.markdown("#### 📝 一页纸摘要")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**公司**: {company_name}")
        st.markdown(f"**行业**: {industry}")
        st.markdown(f"**分析日期**: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    with col2:
        st.markdown(f"**建议**: 谨慎推进")
        st.markdown(f"**风险等级**: 🟡 中等")
        st.markdown(f"**数据完整度**: 65%")
    
    # 详细分析
    if "商业模式画布" in dimensions:
        with st.expander("商业模式画布", expanded=True):
            st.markdown("""
            | 维度 | 内容 |
            |------|------|
            | **价值主张** | 为金融机构提供SaaS解决方案 |
            | **客户细分** | 中小银行、消费金融公司 |
            | **收入来源** | 订阅费60% + 交易佣金30% |
            | **核心资源** | 牌照资质、AI技术 |
            """)
    
    if "风险评估" in dimensions:
        with st.expander("风险评估矩阵", expanded=True):
            risk_df = pd.DataFrame({
                '风险类型': ['关联交易', '客户集中度', '政策风险', '技术迭代', '人员流失'],
                '发生概率': ['高', '中', '中', '低', '中'],
                '影响程度': ['高', '高', '中', '中', '低'],
                '风险等级': ['🔴 高', '🟡 中', '🟡 中', '🟢 低', '🟢 低']
            })
            st.dataframe(risk_df, use_container_width=True, hide_index=True)
    
    # AI增强按钮
    st.markdown("---")
    if st.button("🚀 AI增强尽调分析", type="primary"):
        st.info("调用Gemini AI进行深度分析...")
        
        # 检查API密钥
        if not os.getenv("GEMINI_API_KEY"):
            st.error("⚠️ Gemini API密钥未配置，请在侧边栏设置")
        else:
            st.success("✅ AI分析完成（演示模式）")
            st.markdown("""
            #### 🤖 AI深度分析摘要
            
            **商业模式**: SaaS模式健康，经常性收入占比高，具备长期价值。
            
            **竞争优势**: 在细分领域有一定技术积累，但护城河宽度中等。
            
            **投资风险**: 主要关注关联交易合规性和客户集中度风险。
            
            **投资建议**: 建议谨慎推进，重点补充法律和财务尽调。
            """)
