"""
收并购分析套件 - API模块

提供以下API对接:
- 天眼查 API (TianyanchaAPI): 工商信息、股权结构、法律风险
- Tushare API (TushareFinanceAPI): A股财务数据、估值指标

使用示例:
    from apis import TianyanchaAPI, TushareFinanceAPI
    
    # 天眼查
    tyc = TianyanchaAPI("your_tyc_token")
    info = tyc.get_base_info_v4("公司名称")
    
    # Tushare
    ts = TushareFinanceAPI("your_ts_token")
    df = ts.get_income_statement("600519.SH", "20230101", "20231231")
"""

from .tianyancha_api import TianyanchaAPI
from .tushare_api import TushareFinanceAPI

__all__ = ['TianyanchaAPI', 'TushareFinanceAPI']
__version__ = '1.0.0'
