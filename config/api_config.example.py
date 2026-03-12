"""
API 配置文件示例

使用方法:
1. 复制此文件为 api_config.py
2. 填入你的真实API Token
3. 在代码中导入使用

注意: api_config.py 已加入 .gitignore，不会被提交到Git
"""

# ============================================
# 天眼查 API 配置
# 申请地址: https://open.tianyancha.com/
# ============================================
TIANYANCHA_TOKEN = "your_tianyancha_token_here"

# ============================================
# Tushare API 配置
# 申请地址: https://tushare.pro/register
# ============================================
TUSHARE_TOKEN = "your_tushare_token_here"

# ============================================
# 其他可选API配置
# ============================================

# Wind API (万得) - 机构级数据，需付费
WIND_API_KEY = "your_wind_api_key"

# 同花顺 iFinD API - 机构级数据，需付费
IFIND_API_KEY = "your_ifind_api_key"

# 企查查 API - 类似天眼查
QICHACHA_TOKEN = "your_qichacha_token"

# ============================================
# MCP 服务配置
# ============================================
MCP_SERVERS = {
    "daloopa": {
        "url": "https://mcp.daloopa.com/server/mcp",
        "token": "your_daloopa_token"
    },
    "factset": {
        "url": "https://mcp.factset.com/mcp",
        "token": "your_factset_token"
    }
}
