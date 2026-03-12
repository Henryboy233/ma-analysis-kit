# API 模块说明

本目录包含收并购分析所需的各种API对接模块。

## 模块列表

| 文件 | 功能 | 适用场景 |
|------|------|---------|
| `tianyancha_api.py` | 天眼查API封装 | 非上市公司工商信息、股权结构、法律风险 |
| `tushare_api.py` | Tushare API封装 | A股上市公司财务数据、估值指标 |
| `api_manager.py` | API统一管理器 | 整合多个数据源，统一接口 |
| `__init__.py` | 模块导出 | 简化导入路径 |

## 快速开始

### 1. 安装依赖

```bash
pip install -r ../scripts/requirements.txt
```

### 2. 配置API Token

```bash
# 设置环境变量
export TIANYANCHA_TOKEN="your_tianyancha_token"
export TUSHARE_TOKEN="your_tushare_token"
```

### 3. 使用示例

```python
from apis import TianyanchaAPI, TushareFinanceAPI

# 天眼查 - 非上市公司
 tyc = TianyanchaAPI("your_token")
info = tyc.get_base_info_v4("广东横琴深水云科数字科技有限公司")
shareholders = tyc.get_shareholders("公司名称")

# Tushare - A股上市公司
ts = TushareFinanceAPI("your_token")
income = ts.get_income_statement("600519.SH", "20230101", "20231231")
valuation = ts.get_valuation_metrics("600519.SH")
```

## API 申请地址

### 天眼查
- 官网: https://open.tianyancha.com/
- 费用: 按量计费，约 ¥0.1-1/次
- 覆盖: 全国企业工商信息、法律风险、知识产权

### Tushare
- 官网: https://tushare.pro/register
- 费用: 基础数据免费，高级数据需积分
- 覆盖: A股财务数据、估值指标、行业数据

## 功能对比

| 功能 | 天眼查 | Tushare |
|------|--------|---------|
| 工商信息 | ✅ | ❌ |
| 股权结构 | ✅ | ❌ |
| 法律诉讼 | ✅ | ❌ |
| 财务数据 | ❌ | ✅ |
| 估值指标 | ❌ | ✅ |
| 股价数据 | ❌ | ✅ |

## 适用场景建议

### 分析非上市公司
```python
from apis import TianyanchaAPI

tyc = TianyanchaAPI(token)
result = tyc.full_due_diligence("目标公司名称")
```

### 分析A股上市公司
```python
from apis import TushareFinanceAPI

ts = TushareFinanceAPI(token)
financials = ts.get_full_financials("600519.SH", "20230101", "20231231")
```

### 统一分析（推荐）
```python
from apis.api_manager import APIManager

manager = APIManager()
result = manager.full_analysis("600519.SH", "贵州茅台酒股份有限公司")
summary = manager.generate_report_summary(result)
```

## 错误处理

所有API模块都包含错误处理：
- 网络异常: 返回空结果或错误信息
- API限制: 提示剩余调用次数
- 数据缺失: 返回空DataFrame或None

## 注意事项

1. **Token安全**: 不要硬编码Token，使用环境变量
2. **调用频率**: 注意API的QPS限制，避免被封
3. **数据更新**: 工商数据T+1，财务数据季度更新
4. **数据准确性**: 建议交叉验证关键数据
