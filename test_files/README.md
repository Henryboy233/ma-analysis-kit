# 测试文件说明

本目录包含用于测试商业尽调模块文件解析功能的多种格式测试文件。

## 文件列表

| 文件名 | 格式 | 大小 | 内容说明 |
|--------|------|------|----------|
| `test_document.pdf` | PDF | 1.6 KB | 商业概述文档，包含公司基本信息和商业模式 |
| `test_document.docx` | Word | 36 KB | 公司简介，包含管理团队表格 |
| `test_document.xlsx` | Excel | 6.2 KB | 财务报表和业务指标（多Sheet） |
| `test_presentation.pptx` | PowerPoint | 31 KB | B轮融资路演PPT（5页幻灯片） |
| `test_readme.txt` | 纯文本 | 582 B | 执行摘要说明文档 |

## 测试数据内容

### 公司信息
- **公司名**: Test Tech Co., Ltd. / Test Innovation Ltd.
- **行业**: 金融科技 (Fintech) / 人工智能 (AI)
- **阶段**: Series B / 成长期
- **员工数**: 150人
- **营收**: 6800万 CNY (2024年)

### 核心关键词（用于测试提取功能）
- SaaS解决方案
- AI风控系统
- 银行客户
- 订阅收入
- 风险评分
- 市场扩张

## 使用方法

在**商业尽调**模块中上传这些文件，测试AI分析的文件解析功能：

1. 进入「场景3: 商业尽调」
2. 输入公司名称（如：Test Tech）
3. 上传一个或多个测试文件
4. 点击「开始商业尽调」
5. 验证文件解析结果是否正确显示

## 重新生成

如需重新生成测试文件，运行：

```bash
cd ~/ma-analysis-kit/test_files
source ../venv/bin/activate
python generate_test_files.py
```

## 依赖项

- `fpdf2` - 生成PDF
- `python-docx` - 生成Word
- `pandas` + `openpyxl` - 生成Excel
- `python-pptx` - 生成PowerPoint

---
*Generated for M&A Analysis Kit*
