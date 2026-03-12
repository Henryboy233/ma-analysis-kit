# 智能投研工作台 - 部署与演示指南

> 面向深水云科投资决策场景 | v2.0

---

## 📦 项目结构

```
ma-analysis-kit/
├── app.py                          # Streamlit 主应用
├── app_requirements.txt            # Python 依赖
├── start_app.sh                    # 一键启动脚本
├── config/
│   ├── .env                        # API密钥配置（需创建）
│   ├── data_sources_comparison.csv # 数据源对比
│   └── free_data_sources.csv       # 免费供应商列表
├── apis/                           # API封装模块
│   ├── tushare_api.py              # Tushare财务数据
│   ├── tianyancha_api.py           # 天眼查工商数据
│   └── api_manager.py              # API管理器
├── skills/                         # AI分析技能
│   └── ma-analysis/SKILL.md        # 收并购分析技能
└── README.md                       # 项目文档
```

---

## 🚀 快速部署（5分钟）

### 第一步：环境准备

```bash
# 1. 检查Python版本（需3.9+）
python3 --version

# 2. 进入项目目录
cd ma-analysis-kit

# 3. 创建虚拟环境
python3 -m venv venv

# 4. 激活虚拟环境
source venv/bin/activate  # Mac/Linux
# 或 venv\Scripts\activate  # Windows

# 5. 安装依赖
pip install -r app_requirements.txt
```

### 第二步：配置API密钥

创建 `config/.env` 文件：

```bash
# Tushare API（免费，必需）
# 获取地址：https://tushare.pro/register
TUSHARE_TOKEN=your_tushare_token_here

# 天眼查 API（可选，付费）
# 购买地址：https://open.tianyancha.com/recharge/1
TIANYANCHA_TOKEN=

# 且慢 MCP（已内置）
QIEMAN_API_KEY=zpST_gOMgBPniZGnrHtIaQ
```

### 第三步：启动应用

```bash
./start_app.sh
```

或手动启动：

```bash
source venv/bin/activate
streamlit run app.py --server.port=8501
```

### 第四步：访问应用

浏览器打开：`http://localhost:8501`

---

## 🎯 领导演示流程（10分钟）

### 开场介绍（2分钟）

> **智能投研工作台 v2.0**
> - 基于 Kimi Code + Streamlit 开发
> - 深水云科投资决策场景
> - 三大核心功能：公司分析、组合监控、商业尽调

### 功能演示（8分钟）

#### 1️⃣ 单一公司财务分析（3分钟）

**演示步骤：**
1. 选择「📈 单一公司深度财务分析」
2. 输入股票代码：`600519.SH`（贵州茅台）
3. 点击「🚀 开始分析」

**展示亮点：**
- ✅ 自动获取Tushare真实股价数据
- ✅ K线图 + 20日/60日均线
- ✅ 技术面评分 + 区间涨跌幅
- ✅ 一页纸执行摘要

**话术：**
> "输入股票代码，系统自动获取财务数据和股价走势，生成一页纸的执行摘要，方便领导快速决策。"

---

#### 2️⃣ 投资组合监控（3分钟）

**演示步骤：**
1. 选择「💼 投资组合风险监控」
2. 选择「手动输入」
3. 添加3-4只股票：
   - 600519.SH 贵州茅台 30%
   - 300750.SZ 宁德时代 25%
   - 601318.SH 中国平安 25%
   - 600036.SH 招商银行 20%
4. 点击「🔍 开始组合分析」

**展示亮点：**
- ✅ 组合规模、收益率、最大回撤
- ✅ 行业分布饼图
- ✅ 集中度风险分析
- ✅ VaR风险价值

**话术：**
> "输入持仓明细，系统自动分析组合风险，识别集中度风险，计算VaR值，提供优化建议。"

---

#### 3️⃣ 商业尽调（2分钟）

**演示步骤：**
1. 选择「🔍 智能商业尽调」
2. 输入公司名称：深水云科
3. 选择行业：金融科技
4. 发展阶段：成长期
5. 点击「🚀 开始商业尽调」

**展示亮点：**
- ✅ 商业模式画布
- ✅ 核心竞争力评估
- ✅ 风险矩阵
- ✅ 一页纸尽调报告

**话术：**
> "输入目标公司信息，系统自动生成商业尽调报告，包含商业模式、竞争力、风险评估。"

---

## 📧 邮件功能演示（可选）

**演示步骤：**
1. 侧边栏点击「📧 邮件配置」
2. 展开「🔐 配置发件邮箱」
3. 输入测试邮箱：`liugs3@infore.com`
4. 点击「🚀 发送测试邮件」

**展示效果：**
- 实时发送邮件到指定邮箱
- HTML格式邮件内容
- 包含发送时间、配置信息

---

## 🆓 免费数据源展示

**侧边栏点击「🆓 查看免费数据源」**

核心免费供应商：
| 供应商 | 数据类型 | 优先级 |
|--------|---------|--------|
| Tushare | A股财务数据 | P0 |
| AKShare | 股票/基金/期货 | P1 |
| 且慢MCP | 基金数据 | P0 |
| 巨潮资讯网 | 上市公司公告 | P2 |
| 裁判文书网 | 法律诉讼 | P2 |

---

## 🔧 常见问题

### Q1: Tushare Token如何获取？
1. 访问 https://tushare.pro/register
2. 手机注册，免费获取Token
3. 新用户送200积分

### Q2: 显示"未找到财务数据"？
- 原因：Tushare积分不足（财务数据需要2000积分）
- 解决：
  - 充值20元获取2000+积分
  - 或先使用股价技术分析（120积分即可）

### Q3: 天眼查数据如何获取？
- 访问 https://open.tianyancha.com/recharge/1
- 推荐套餐：7500元/5万次（0.15元/次）

### Q4: 如何部署到其他服务器？
```bash
# 1. 打包项目
tar -czvf ma-analysis-kit.tar.gz ma-analysis-kit/

# 2. 传输到目标服务器
scp ma-analysis-kit.tar.gz user@server:/path/

# 3. 解压并部署
tar -xzvf ma-analysis-kit.tar.gz
cd ma-analysis-kit
./start_app.sh
```

---

## 📊 数据源成本对比

| 数据源 | 费用 | 覆盖内容 | 推荐指数 |
|--------|------|---------|----------|
| Tushare | 免费/积分 | A股财务 | ⭐⭐⭐⭐⭐ |
| 天眼查 | ¥0.15/次 | 工商/股权 | ⭐⭐⭐⭐⭐ |
| 且慢MCP | 免费 | 基金数据 | ⭐⭐⭐⭐⭐ |
| Wind | ¥3-8万/年 | 全品种 | ⭐⭐⭐⭐ |

---

## 📝 演示 checklist

- [ ] 应用能正常启动
- [ ] Tushare Token已配置
- [ ] 能获取茅台股价数据
- [ ] 能显示K线图和均线
- [ ] 投资组合分析正常
- [ ] 商业尽调报告生成正常
- [ ] 邮件发送功能正常（可选）

---

**祝演示顺利！🎉**
