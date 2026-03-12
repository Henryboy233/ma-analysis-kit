# 收并购分析资源大全 - 直接"抄作业"

> 社区已实现的金融分析Skill、Prompt模板、工具汇总

---

## 一、可直接复制的Prompt模板

### 1. 工商尽调Prompt（天眼查风格）

```markdown
作为资深投行分析师，请对[公司名称]进行工商尽职调查：

1. 基本信息核查
   - 注册信息：成立时间、注册资本、实缴资本、法定代表人
   - 股权结构：股东列表、持股比例、实际控制人穿透
   - 历史沿革：重大工商变更、曾用名

2. 法律风险扫描
   - 法律诉讼：案件数量、案由、金额、身份（原告/被告）
   - 被执行人：执行金额、案件状态
   - 失信记录：是否失信被执行人
   - 经营异常：列入原因、是否移出
   - 行政处罚：处罚事由、金额、时间

3. 关联关系
   - 对外投资：子公司、参股公司
   - 分支机构：分公司、办事处
   - 疑似关联方：同电话/同地址企业

4. 知识产权
   - 专利数量、类型
   - 商标情况
   - 软件著作权

输出格式：Markdown表格 + 风险等级标注（高/中/低）
```

### 2. 财务分析Prompt（财务尽调风格）

```markdown
作为财务尽调专家，请分析以下财务数据：

数据范围：[上传Excel或提供数据]

分析维度：
1. 盈利能力
   - 收入增长率（近3年）
   - 毛利率趋势
   - 净利率变化
   - ROE/ROA

2. 偿债能力
   - 资产负债率
   - 流动比率/速动比率
   - 利息保障倍数

3. 营运能力
   - 应收账款周转天数
   - 存货周转天数
   - 现金转换周期

4. 现金流
   - 经营活动现金流净额
   - 自由现金流
   - 现金收入比

5. Red Flags识别
   - 收入确认异常信号
   - 关联交易占比
   - 应收账款异常增长
   - 存货跌价风险
   - 表外负债迹象

输出要求：
- 关键发现用🔴🟡🟢标注风险等级
- 提供与行业平均值的对比
- 列出需要管理层解释的3-5个问题
```

### 3. 估值分析Prompt（投行建模风格）

```markdown
作为估值分析师，请使用[DCF/可比公司法/先例交易法]对[公司名称]进行估值：

DCF模型（如适用）：
- 预测期：5年
- 收入增长率假设：[用户输入或基于历史]
- 毛利率假设：[用户输入或基于历史]
- 费用率假设：[销售/管理/研发费用率]
- 折现率(WACC)：[计算或假设]
- 永续增长率：[2-3%]

可比公司法：
- 选取3-5家可比公司
- 对比PE、EV/EBITDA、P/S倍数
- 考虑流动性折价/控制权溢价

敏感性分析：
- 不同增长率情景下的估值
- 不同折现率下的估值

输出：
- 估值区间（保守/基准/乐观）
- 关键假设说明
- 风险提示
```

### 4. 基金分析Prompt（且慢MCP风格）

```markdown
使用且慢MCP工具分析以下基金：

基金列表：[基金名称/代码]

分析内容：
1. 基本信息
   - 基金类型、成立时间、规模
   - 基金经理、管理公司
   - 费率结构

2. 业绩分析
   - 近1/3/5年收益率
   - 与基准/同类排名
   - 最大回撤、夏普比率

3. 持仓分析
   - 前十大重仓股/债券
   - 行业分布
   - 集中度风险

4. 适用性评估
   - 风险等级匹配
   - 投资期限匹配
   - 与现有组合的互补性

使用 @qieman 工具获取实时数据。
```

---

## 二、社区现成的Skill/Agent（直接可用）

### 国内平台

#### 1. 阿里云百炼 - 且慢MCP ⭐⭐⭐⭐⭐
- **地址**: https://www.aliyun.com/product/bailian
- **成本**: 免费
- **功能**: 基金数据、投研分析、资产配置
- **接入**: 已在你的Kimi Code配置
- **状态**: ✅ 已就绪

#### 2. 百度智能云千帆 - 且慢MCP
- **地址**: https://qianfan.cloud.baidu.com/
- **成本**: 免费
- **功能**: 同上，多一个平台选择

#### 3. 火山引擎 - 且慢MCP
- **地址**: https://www.volcengine.com/product/mcp
- **成本**: 免费
- **功能**: 同上，支持扣子(Coze)平台

### 国际平台（适合美股/出海项目）

#### 4. Daloopa MCP ⭐⭐⭐⭐
- **地址**: https://daloopa.com/mcp
- **成本**: 付费（$500+/月）
- **功能**: 美股财务数据、SEC文件、投研分析
- **适用**: 中概股、美股并购

#### 5. Financial Modeling Prep MCP
- **地址**: https://site.financialmodelingprep.com/
- **成本**: 免费+付费
- **功能**: 全球股票数据、财报、估值

#### 6. Bloomberg MCP (Alpha)
- **地址**: 需申请
- **成本**: 极高（终端年费）
- **功能**: 机构级金融数据

---

## 三、开源项目/GitHub资源

### Python工具库

#### 1. AKShare ⭐⭐⭐⭐⭐
```bash
pip install akshare
```
- **GitHub**: https://github.com/akfamily/akshare
- **功能**: 免费金融数据接口（A股、期货、外汇、宏观）
- **适用**: Tushare的免费替代
- **文档**: https://www.akshare.xyz/

#### 2. Tushare
```bash
pip install tushare
```
- **官网**: https://tushare.pro/
- **功能**: A股财务数据、行情、基本面
- **成本**: 基础免费，高级需积分

#### 3. Qichacha API SDK
```bash
pip install qichacha
```
- **功能**: 企查查API封装
- **适用**: 工商信息查询

### MCP Server开源实现

#### 4. Tianyancha MCP Server（社区版）
```bash
# GitHub搜索: tianyancha mcp server
# 有多个开源实现，可自行部署
```

#### 5. 通用Finance MCP
- **awesome-mcp-servers**: https://github.com/punkpeye/awesome-mcp-servers
- 搜索"finance"分类

---

## 四、专业数据平台（付费但值得）

### 一级市场创投

| 平台 | 网址 | 成本 | 用途 |
|------|------|------|------|
| IT桔子 | https://www.itjuzi.com/ | ¥5000/年 | 融资事件、独角兽 |
| 36氪创投 | https://36kr.com/ | 免费+付费 | 早期项目 |
| 鲸准 | https://www.jingdata.com/ | ¥1万+/年 | 项目库、LP/GP |
| 清科私募通 | 需联系销售 | 定制 | PE/VC基金 |

### 行业研究

| 平台 | 网址 | 成本 | 用途 |
|------|------|------|------|
| 艾瑞咨询 | https://www.iresearch.com.cn/ | 免费报告 | 互联网/TMT |
| 易观分析 | https://www.analysys.cn/ | 免费报告 | 金融科技 |
| 前瞻产业研究院 | https://www.qianzhan.com/ | 付费 | 行业报告 |
| 头豹研究院 | https://www.leadleo.com/ | 付费 | 细分行业 |

### 法律/合规

| 平台 | 网址 | 成本 | 用途 |
|------|------|------|------|
| 北大法宝 | https://www.pkulaw.com/ | ¥5000+/年 | 法律法规、案例 |
| 威科先行 | https://law.wkinfo.com.cn/ | ¥1万+/年 | 合规实务 |
| 无讼案例 | https://www.itslaw.com/ | 免费+付费 | 判例检索 |

---

## 五、Prompt Engineering资源

### 学习资源

1. **OpenAI Prompt Engineering Guide**
   - https://platform.openai.com/docs/guides/prompt-engineering

2. **Claude Prompt Library**
   - https://docs.anthropic.com/en/prompt-library

3. **LangChain Prompt Templates**
   - https://python.langangchain.com/docs/modules/model_io/prompts/

### 金融专项

4. **FinGPT Prompts**
   - GitHub: https://github.com/AI4Finance-Foundation/FinGPT
   - 金融大模型的Prompt集合

5. **BloombergGPT相关论文**
   - 搜索金融NLP、金融问答Prompt设计

---

## 六、推荐组合（按场景）

### 场景1：国内非上市公司收并购
```yaml
已配置:
  - 且慢MCP (免费) ✅

立即申请:
  - 天眼查 API (¥7500/年)
  - Tushare (免费)

辅助工具:
  - AKShare (免费备用)
  - 裁判文书网 (免费)
```

### 场景2：A股上市公司分析
```yaml
核心:
  - Tushare (免费)
  - 且慢MCP (免费) ✅
  - 巨潮资讯网 (免费公告)

增强:
  - Wind/iFinD (付费终端)
  - 慧博投研 (研报)
```

### 场景3：跨境并购（含海外标的）
```yaml
国内:
  - 天眼查 API
  - Tushare

国际:
  - Daloopa MCP (付费)
  - Financial Modeling Prep
  - Crunchbase (创投)
```

---

## 七、快速开始清单

### 今天可以做的事

- [x] 且慢MCP已配置 ✅
- [ ] 申请天眼查API（1-3天审批）
- [ ] 注册Tushare账号（即时）
- [ ] 安装AKShare备用（5分钟）
- [ ] 测试分析一家公司（30分钟）

### 本周内完成

- [ ] 跑通天眼查API调用
- [ ] 整合内部资料分析流程
- [ ] 生成第一份完整报告
- [ ] 评估是否需要Wind/iFinD

---

## 八、求助渠道

### 技术支持
- **Kimi Code文档**: https://kimi.com/docs
- **MCP协议规范**: https://modelcontextprotocol.io/
- **天眼查开放平台**: https://open.tianyancha.com/

### 社区交流
- **知乎**: 搜索"投研自动化"、"MCP金融"
- **GitHub Discussions**: MCP相关项目
- **飞书文档**: 且慢MCP使用指南（已发你）

---

**总结**: 你现在已经有了
1. ✅ 且慢MCP（基金分析，免费）
2. ✅ 完整的收并购Skill定义
3. ✅ 可直接复制的Prompt模板
4. ⏳ 待申请：天眼查API + Tushare

下一步：申请天眼查API，跑通第一个完整分析！
