# 安全说明

## API密钥管理

本项目所有API密钥均通过**环境变量**读取，代码中**不包含任何硬编码密钥**。

### 支持的API密钥

| 服务 | 环境变量名 | 说明 |
|------|-----------|------|
| Gemini AI | `GEMINI_API_KEY` | AI尽调分析（可选，有默认值） |
| Tushare | `TUSHARE_TOKEN` | A股财务数据（可选） |
| 天眼查 | `TIANYANCHA_TOKEN` | 企业工商信息（可选） |

### 配置方法

创建 `.env` 文件（已添加到 .gitignore，不会被提交）：

```bash
# config/.env
TUSHARE_TOKEN=your_tushare_token
TIANYANCHA_TOKEN=your_tianyancha_token
GEMINI_API_KEY=your_gemini_api_key
```

或在启动前设置环境变量：

```bash
export TUSHARE_TOKEN="your_token"
export TIANYANCHA_TOKEN="your_token"
export GEMINI_API_KEY="your_key"
streamlit run app.py
```

## 安全警告

⚠️ **切勿将API密钥提交到Git仓库！**

- `.env` 文件已添加到 `.gitignore`
- 所有密钥读取使用 `os.getenv()`
- 代码中不包含任何真实密钥

如发现密钥泄漏，请立即：
1. 撤销并重新生成API密钥
2. 从GitHub历史中删除（使用 git-filter-repo）
3. 强制推送更新后的代码

## 报告安全问题

如发现安全漏洞，请通过以下方式联系：
- GitHub Issues
- 邮件：henryliu233@qq.com
