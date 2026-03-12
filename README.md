# 🏢 智能投研工作台 (M&A Analysis Kit)

基于Streamlit的智能投研分析系统，专为收并购(M&A)场景设计，提供企业财务分析、投资组合监控和商业尽调(CDD)功能。

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ 核心功能

### 📈 场景一：单一公司深度财务分析
- **多数据源支持**：AKShare（免费）+ Tushare（备用）
- **财务健康度评分**：基于多维度指标的综合评估
- **可视化图表**：营收趋势、盈利能力、估值分析
- **风险排雷**：自动识别财务异常和风险点

### 📊 场景二：投资组合监控
- **组合分析**：持仓分布、行业配置、相关性分析
- **实时数据**：股价查询和收益率计算
- **风险监控**：集中度风险、VaR风险价值
- **自动报告**：邮件通知和定期报告生成

### 🔍 场景三：智能商业尽调(CDD)
- **文件解析**：支持PDF、Word、Excel、PPT自动解析
- **AI增强分析**：集成Gemini 3.1 Pro进行深度尽调
- **流式输出**：实时显示AI分析结果
- **多维度评估**：商业模式、竞争优势、风险评估、投资建议

## 🚀 快速开始

### 环境要求
- Python 3.9+
- macOS / Linux / Windows

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/ma-analysis-kit.git
cd ma-analysis-kit

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量（可选）
cp config/.env.example config/.env
# 编辑 .env 文件添加API密钥

# 5. 启动应用
streamlit run app.py
```

访问 http://localhost:8501 开始使用。

## 📋 依赖说明

### 主要依赖
```
streamlit>=1.28.0
pandas>=1.5.0
plotly>=5.15.0
akshare>=1.11.0
tushare>=1.2.89
requests>=2.31.0
python-dotenv>=1.0.0
```

### 文件解析依赖
```
PyMuPDF>=1.23.0      # PDF解析
python-docx>=0.8.11  # Word解析
openpyxl>=3.1.0      # Excel解析
python-pptx>=0.6.21  # PPT解析
```

## 🔑 API配置（可选）

| 服务 | 用途 | 获取方式 |
|------|------|----------|
| Tushare | A股财务数据 | https://tushare.pro/register |
| Gemini | AI尽调分析 | https://makersuite.google.com/app/apikey |
| 天眼查 | 企业工商信息 | https://open.tianyancha.com/ |

编辑 `config/.env` 文件配置API密钥：
```bash
TUSHARE_TOKEN=your_token_here
TIANYANCHA_TOKEN=your_token_here
```

## 📁 项目结构

```
ma-analysis-kit/
├── app.py                 # 主应用入口
├── requirements.txt       # Python依赖
├── README.md             # 项目说明
├── .gitignore            # Git忽略规则
├── config/               # 配置文件
│   └── .env              # 环境变量
├── apis/                 # API封装模块
│   ├── akshare_api.py    # AKShare免费数据
│   ├── tushare_api.py    # Tushare数据
│   ├── gemini_api.py     # Gemini AI分析
│   └── tianyancha_api.py # 天眼查工商数据
└── test_files/           # 测试文件
    ├── test_document.pdf
    ├── test_document.docx
    ├── test_document.xlsx
    └── test_presentation.pptx
```

## 🖥️ 使用指南

### 单一公司分析
1. 选择「场景一：单一公司深度财务分析」
2. 输入股票代码（如：600519.SH）或公司名称
3. 选择数据源（推荐AKShare免费版）
4. 点击「开始分析」

### 投资组合监控
1. 选择「场景二：投资组合监控」
2. 输入持仓信息（支持CSV导入）
3. 查看组合分析和风险评估

### 商业尽调
1. 选择「场景三：商业尽调」
2. 输入目标公司信息
3. 上传尽调资料（PDF/Word/Excel/PPT）
4. 点击「开始商业尽调」
5. 使用「AI增强分析」获取深度洞察

## 🧪 测试文件

项目包含多格式测试文件，位于 `test_files/` 目录：
- `test_document.pdf` - 商业概述
- `test_document.docx` - 公司简介
- `test_document.xlsx` - 财务数据
- `test_presentation.pptx` - 融资路演
- `test_readme.txt` - 执行摘要

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 数据来源：[AKShare](https://www.akshare.xyz/)、[Tushare](https://tushare.pro/)
- AI能力：[Google Gemini](https://deepmind.google/technologies/gemini/)
- UI框架：[Streamlit](https://streamlit.io/)

---

<p align="center">Made with ❤️ for M&A Professionals</p>
