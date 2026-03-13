#!/usr/bin/env python3
"""
Agent管理平台
整合多个专业Agent，提供统一入口
"""

import streamlit as st
import os
import sys
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="Agent管理平台",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin: 10px 0;
        cursor: pointer;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .agent-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .agent-icon {
        font-size: 3rem;
        margin-bottom: 15px;
    }
    .agent-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .agent-desc {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 50px;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 50px;
    }
    .stButton>button {
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ==================== Agent管理总页面 ====================

def agent_manager():
    """Agent管理总页面"""
    
    st.title("🤖 Agent 管理平台")
    st.markdown("选择专业Agent开始工作，或直接与通用助手对话")
    
    # Agent选择
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="agent-card" onclick="">
            <div class="agent-icon">💰</div>
            <div class="agent-title">金融Agent</div>
            <div class="agent-desc">
                • 单一公司财务分析<br>
                • 投资组合监控<br>
                • 商业尽调(CDD)<br>
                • AI增强分析
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入金融Agent", key="btn_finance", use_container_width=True):
            st.session_state.current_agent = "finance"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="agent-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <div class="agent-icon">🎯</div>
            <div class="agent-title">基础Claw</div>
            <div class="agent-desc">
                • 通用对话交互<br>
                • 代码编写辅助<br>
                • 问题诊断解决<br>
                • 文件处理分析
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入基础Claw", key="btn_claw", use_container_width=True):
            st.session_state.current_agent = "claw"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="agent-card" style="background: linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%);">
            <div class="agent-icon">🚀</div>
            <div class="agent-title">AI增强</div>
            <div class="agent-desc">
                • Gemini 3.1 Pro<br>
                • 深度分析能力<br>
                • 流式实时响应<br>
                • 专业报告生成
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("进入AI增强", key="btn_ai", use_container_width=True):
            st.session_state.current_agent = "ai_enhanced"
            st.rerun()
    
    # 快捷对话区域
    st.markdown("---")
    st.subheader("💬 快速对话")
    st.info("👇 在此输入问题，系统将自动分配合适的Agent处理")
    
    # 智能路由对话
    quick_chat_interface()

# ==================== 金融Agent ====================

def finance_agent():
    """金融Agent - 封装现有的3个场景"""
    
    st.title("💰 金融Agent")
    st.markdown("专业投资分析助手，提供财务分析、组合监控、商业尽调服务")
    
    # 子场景选择
    tab1, tab2, tab3, tab_chat = st.tabs([
        "📈 公司财务分析", 
        "📊 投资组合监控", 
        "🔍 商业尽调",
        "💬 自由对话"
    ])
    
    with tab1:
        from agents.finance_agent import company_analysis_mode
        company_analysis_mode()
    
    with tab2:
        from agents.finance_agent import portfolio_monitor_mode
        portfolio_monitor_mode()
    
    with tab3:
        from agents.finance_agent import due_diligence_mode
        due_diligence_mode()
    
    with tab_chat:
        finance_chat_mode()
    
    # 返回按钮
    if st.sidebar.button("← 返回Agent管理", use_container_width=True):
        st.session_state.current_agent = "manager"
        st.rerun()

def finance_chat_mode():
    """金融Agent对话模式"""
    st.subheader("💬 金融分析对话")
    st.markdown("直接告诉我你想分析什么，例如：")
    st.markdown("- \"分析贵州茅台的财务状况\"")
    st.markdown("- \"帮我看看这个投资组合\"")
    st.markdown("- \"对这家公司进行尽调\"")
    
    # 初始化对话历史
    if 'finance_chat_history' not in st.session_state:
        st.session_state.finance_chat_history = []
    
    # 显示历史
    for msg in st.session_state.finance_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # 输入框
    if prompt := st.chat_input("输入你的金融分析问题..."):
        # 用户消息
        st.session_state.finance_chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI响应
        with st.chat_message("assistant"):
            response = route_finance_query(prompt)
            st.markdown(response)
            st.session_state.finance_chat_history.append({"role": "assistant", "content": response})

def route_finance_query(query: str) -> str:
    """路由金融查询到对应功能"""
    query = query.lower()
    
    if any(kw in query for kw in ["股票", "公司", "财务", "600", "茅台", "分析"]):
        return "📈 **建议切换到「公司财务分析」标签页**\n\n我检测到您想进行公司财务分析。请提供：\n- 股票代码（如：600519.SH）\n- 或公司名称\n\n我将为您获取财务数据并生成健康度报告。"
    
    elif any(kw in query for kw in ["组合", "持仓", "投资", "监控", "风险"]):
        return "📊 **建议切换到「投资组合监控」标签页**\n\n我检测到您想监控投资组合。请：\n- 上传持仓CSV文件\n- 或手动输入持仓信息\n\n我将为您分析组合风险和收益。"
    
    elif any(kw in query for kw in ["尽调", "cdd", "收购", "并购", "尽调资料"]):
        return "🔍 **建议切换到「商业尽调」标签页**\n\n我检测到您想进行商业尽调。请：\n- 输入目标公司名称\n- 上传尽调资料（PDF/Word/Excel/PPT）\n\n我将为您生成尽调报告并提供AI增强分析。"
    
    else:
        return "🤖 我是金融Agent，专注于以下领域：\n\n1. **公司财务分析** - 分析上市公司财务状况\n2. **投资组合监控** - 监控多资产组合表现\n3. **商业尽调** - AI辅助商业尽调分析\n\n请告诉我您需要哪方面的帮助，或直接切换到对应标签页。"

# ==================== 基础Claw Agent ====================

def claw_agent():
    """基础Claw Agent - 通用对话交互"""
    
    st.title("🎯 基础Claw")
    st.markdown("通用AI助手，支持代码编写、问题诊断、文件处理等多种任务")
    
    # 初始化对话历史
    if 'claw_chat_history' not in st.session_state:
        st.session_state.claw_chat_history = [
            {"role": "assistant", "content": "👋 你好！我是基础Claw，你的通用AI助手。\n\n我可以帮你：\n• 编写和调试代码\n• 分析处理文件\n• 解答技术问题\n• 提供建议和方案\n\n有什么可以帮你的吗？"}
        ]
    
    # 显示对话历史
    for msg in st.session_state.claw_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # 用户输入
    if prompt := st.chat_input("输入你的问题...", key="claw_input"):
        # 添加用户消息
        st.session_state.claw_chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 生成响应
        with st.chat_message("assistant"):
            response = generate_claw_response(prompt)
            st.markdown(response)
            st.session_state.claw_chat_history.append({"role": "assistant", "content": response})
    
    # 工具箱
    with st.sidebar:
        st.subheader("🧰 工具箱")
        
        if st.button("📝 代码助手"):
            st.session_state.claw_chat_history.append({
                "role": "assistant", 
                "content": "💻 **代码助手模式**\n\n请描述你需要编写的代码功能，或粘贴需要调试的代码。"
            })
            st.rerun()
        
        if st.button("📄 文件分析"):
            uploaded = st.file_uploader("上传文件", type=['py', 'txt', 'md', 'json', 'csv'])
            if uploaded:
                content = uploaded.read().decode('utf-8')[:3000]
                st.session_state.claw_chat_history.append({
                    "role": "user",
                    "content": f"请分析这个文件（{uploaded.name}）：\n```\n{content}\n```"
                })
                st.rerun()
        
        if st.button("🔄 清空对话"):
            st.session_state.claw_chat_history = []
            st.rerun()
        
        st.markdown("---")
        if st.button("← 返回Agent管理", use_container_width=True):
            st.session_state.current_agent = "manager"
            st.rerun()

def generate_claw_response(prompt: str) -> str:
    """生成Claw响应（模拟，实际可接入本地模型或API）"""
    
    # 这里可以接入实际的AI模型
    # 当前使用基于规则的响应作为演示
    
    prompt_lower = prompt.lower()
    
    if any(kw in prompt_lower for kw in ["代码", "python", "编写", "函数"]):
        return """💻 我来帮你编写代码！\n\n基于你的需求，我建议以下实现：\n
```python
def example_function():
    \"\"\"
    示例函数
    \"\"\"
    pass
```
\n需要我详细解释或修改吗？"""
    
    elif any(kw in prompt_lower for kw in ["错误", "报错", "exception", "bug"]):
        return """🔧 看起来你遇到了问题！\n\n请提供：\n1. 完整的错误信息（包括Traceback）\n2. 相关的代码片段\n3. 你期望的行为\n\n我会帮你诊断并给出解决方案。"""
    
    elif any(kw in prompt_lower for kw in ["你好", "嗨", "hello", "hi"]):
        return "👋 你好！很高兴为你服务。有什么我可以帮助你的吗？"
    
    else:
        return """🤔 收到你的问题！\n\n作为基础Claw，我可以帮你：\n• 编写和解释代码\n• 分析文件内容\n• 诊断技术问题\n• 提供实现建议\n\n请详细描述你的需求，我会尽力协助。"""

# ==================== AI增强Agent ====================

def ai_enhanced_agent():
    """AI增强Agent - Gemini深度对话"""
    
    st.title("🚀 AI增强 Agent")
    st.markdown("基于 **Gemini 3.1 Pro** 的深度分析助手，提供专业的报告生成和分析能力")
    
    # API密钥检查
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        st.warning("⚠️ Gemini API密钥未配置")
        with st.expander("配置API密钥"):
            key_input = st.text_input("输入Gemini API密钥", type="password")
            if key_input:
                os.environ["GEMINI_API_KEY"] = key_input
                st.success("✅ 已配置（当前会话有效）")
                st.rerun()
    
    # 初始化对话历史
    if 'ai_chat_history' not in st.session_state:
        st.session_state.ai_chat_history = [
            {"role": "assistant", "content": "🚀 你好！我是AI增强Agent，基于Gemini 3.1 Pro。\n\n我擅长：\n• 深度分析报告生成\n• 商业尽调分析\n• 专业文档撰写\n• 复杂问题推理\n\n请告诉我你需要什么专业分析？"}
        ]
    
    # 显示对话历史
    for msg in st.session_state.ai_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # 用户输入
    if prompt := st.chat_input("输入你的问题...", key="ai_input"):
        # 添加用户消息
        st.session_state.ai_chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 流式生成响应
        with st.chat_message("assistant"):
            if api_key:
                stream_gemini_response(prompt)
            else:
                response = "⚠️ 请先在侧边栏配置Gemini API密钥以使用AI增强功能。"
                st.markdown(response)
                st.session_state.ai_chat_history.append({"role": "assistant", "content": response})
    
    # 侧边栏工具
    with st.sidebar:
        st.subheader("⚙️ 设置")
        
        # 模型选择
        model = st.selectbox(
            "模型",
            ["gemini-3.1-pro-preview", "gemini-2.0-flash"],
            index=0
        )
        
        # 温度设置
        temperature = st.slider("创造性", 0.0, 1.0, 0.7)
        
        st.markdown("---")
        
        if st.button("🔄 清空对话"):
            st.session_state.ai_chat_history = []
            st.rerun()
        
        if st.button("← 返回Agent管理", use_container_width=True):
            st.session_state.current_agent = "manager"
            st.rerun()

def stream_gemini_response(prompt: str):
    """流式调用Gemini API"""
    from apis.gemini_api import GeminiAnalyzer
    
    try:
        gemini = GeminiAnalyzer()
        
        # 构建带历史记录的提示
        history = "\n".join([
            f"{'用户' if msg['role'] == 'user' else '助手'}: {msg['content']}"
            for msg in st.session_state.ai_chat_history[-5:]  # 最近5轮
        ])
        
        full_prompt = f"""历史对话：
{history}

当前问题：{prompt}

请基于上下文回答。"""
        
        # 流式生成
        response_placeholder = st.empty()
        full_response = ""
        
        # 使用非流式API（简化）
        response = gemini._call_api(full_prompt)
        
        if response.startswith("API调用失败") or response.startswith("❌"):
            st.error(response)
            st.session_state.ai_chat_history.append({"role": "assistant", "content": response})
        else:
            # 模拟打字机效果
            for i in range(0, len(response), 5):
                partial = response[:i+5]
                response_placeholder.markdown(partial + "▌")
            
            response_placeholder.markdown(response)
            st.session_state.ai_chat_history.append({"role": "assistant", "content": response})
            
    except Exception as e:
        error_msg = f"❌ 调用失败: {str(e)}"
        st.error(error_msg)
        st.session_state.ai_chat_history.append({"role": "assistant", "content": error_msg})

# ==================== 快速对话界面 ====================

def quick_chat_interface():
    """首页快速对话"""
    
    # 初始化
    if 'quick_chat' not in st.session_state:
        st.session_state.quick_chat = []
    
    # 显示历史（只显示最近2轮）
    for msg in st.session_state.quick_chat[-4:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # 输入
    if prompt := st.chat_input("输入问题，系统自动分配合适的Agent...", key="quick_input"):
        # 用户消息
        st.session_state.quick_chat.append({"role": "user", "content": prompt})
        
        # 智能路由
        with st.chat_message("assistant"):
            route = analyze_intent(prompt)
            
            if route["agent"] == "finance":
                st.markdown(f"💰 **已为您调度金融Agent**\n\n{route['response']}")
                if st.button("立即进入金融Agent →", key="route_finance"):
                    st.session_state.current_agent = "finance"
                    st.rerun()
            
            elif route["agent"] == "claw":
                st.markdown(f"🎯 **已为您调度基础Claw**\n\n{route['response']}")
                if st.button("立即进入基础Claw →", key="route_claw"):
                    st.session_state.current_agent = "claw"
                    st.rerun()
            
            elif route["agent"] == "ai":
                st.markdown(f"🚀 **已为您调度AI增强**\n\n{route['response']}")
                if st.button("立即进入AI增强 →", key="route_ai"):
                    st.session_state.current_agent = "ai_enhanced"
                    st.rerun()
            
            st.session_state.quick_chat.append({
                "role": "assistant", 
                "content": route['response']
            })

def analyze_intent(prompt: str) -> dict:
    """分析用户意图，路由到合适Agent"""
    prompt_lower = prompt.lower()
    
    # 金融相关
    finance_keywords = ["股票", "财报", "财务", "投资", "组合", "尽调", "并购", "cdd", "600", "茅台", "上市", "营收", "利润", "估值"]
    if any(kw in prompt_lower for kw in finance_keywords):
        return {
            "agent": "finance",
            "response": "检测到金融分析需求。金融Agent提供：\n• 公司财务深度分析\n• 投资组合监控\n• 商业尽调(CDD)\n\n点击下方按钮进入专业金融分析界面。"
        }
    
    # 代码/技术相关
    tech_keywords = ["代码", "python", "bug", "错误", "调试", "函数", "类", "import", "报错", "exception"]
    if any(kw in prompt_lower for kw in tech_keywords):
        return {
            "agent": "claw",
            "response": "检测到技术开发需求。基础Claw可以：\n• 编写和调试代码\n• 分析错误日志\n• 提供技术方案\n\n点击下方按钮进入开发助手界面。"
        }
    
    # 分析/报告相关
    analysis_keywords = ["分析", "报告", "撰写", "总结", "评估", "研究", "深度"]
    if any(kw in prompt_lower for kw in analysis_keywords):
        return {
            "agent": "ai",
            "response": "检测到深度分析需求。AI增强Agent基于Gemini 3.1 Pro，提供：\n• 专业报告生成\n• 深度分析推理\n• 高质量文案撰写\n\n点击下方按钮进入AI增强界面。"
        }
    
    # 默认
    return {
        "agent": "claw",
        "response": "我是Agent调度助手。根据您的问题，建议：\n• 💰 金融分析 → 金融Agent\n• 🎯 技术开发 → 基础Claw\n• 🚀 深度分析 → AI增强\n\n或点击上方卡片选择专业Agent。"
    }

# ==================== 主入口 ====================

def main():
    """主入口"""
    
    # 初始化当前Agent
    if 'current_agent' not in st.session_state:
        st.session_state.current_agent = "manager"
    
    # 路由到对应Agent
    if st.session_state.current_agent == "manager":
        agent_manager()
    elif st.session_state.current_agent == "finance":
        finance_agent()
    elif st.session_state.current_agent == "claw":
        claw_agent()
    elif st.session_state.current_agent == "ai_enhanced":
        ai_enhanced_agent()

if __name__ == "__main__":
    main()
