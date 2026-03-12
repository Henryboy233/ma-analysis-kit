# OpenClaw 社区金融分析 Skill 清单

> 调研日期：2026-03-12
> 来源：OpenClaw社区、华创证券、阿里云等

---

## 🌟 核心推荐 Skill

### 1. Day1Global-Skills（顶级推荐）

**GitHub**: https://github.com/star23/Day1Global-Skills

**简介**: 由Day1Global团队开发的美股财报分析Skill

**16个分析模块**: 收入质量、盈利能力、现金流量、竞争格局、估值模型等

**6种投资哲学**: 巴菲特式、费雪式、格雷厄姆式、催化剂驱动等

**复用建议**: ⭐⭐⭐⭐⭐

---

### 2. financial-analysis（财务分析）

**安装**: `clawhub install financial-analysis`

**功能**: A股/美股基本面分析、DCF估值、Excel估值表

**复用建议**: ⭐⭐⭐⭐

---

### 3. equity-research（股票研究）

**安装**: `clawhub install equity-research`

**功能**: 深度个股研究、行业对比、财务建模

**复用建议**: ⭐⭐⭐⭐

---

## 📊 数据获取类

### 4. Stock-Watcher（股票监控）

**功能**: 自选股管理、价格监控、异常提醒

**复用建议**: ⭐⭐⭐⭐⭐

---

### 5. Tavily Search（精准搜索）

**安装**: `clawhub install tavily-search`

**功能**: 网页搜索、新闻抓取、研报搜索

**复用建议**: ⭐⭐⭐⭐

---

## 🤖 自动化类

### 6. Self-Improvement Skill

**GitHub**: https://github.com/peterskoett/self-improving-agent

**功能**: 反思学习、错误记录、自动优化

---

### 7. Summarize（长文本提炼）

**安装**: `clawhub install summarize`

**功能**: 文本摘要、研报核心观点提取

**复用建议**: ⭐⭐⭐⭐⭐

---

### 8. Office-Automation（办公自动化）

**安装**: `clawhub install office-automation`

**功能**: Excel/Word/PPT自动化

---

## 🔌 MCP 服务

### 9. 且慢MCP（盈米）✅ 已接入

**官网**: https://qieman.com/mcp

**功能**: 基金查询、组合诊断、资产配置

**费用**: 免费

---

## 🎯 推荐组合

### 基础财务分析
```bash
clawhub install financial-analysis stock-watcher summarize
```

### 深度投研
```bash
clawhub install financial-analysis equity-research tavily-search office-automation
```
