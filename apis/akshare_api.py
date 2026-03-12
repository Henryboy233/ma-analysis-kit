#!/usr/bin/env python3
"""
AKShare API 对接模块
免费A股财务数据替代方案

功能:
- A股财务数据获取（利润表、资产负债表、现金流量表）
- 完全免费，无需积分
- 作为Tushare的免费备用方案

使用:
    from apis.akshare_api import AKShareFinanceAPI
    
    ak_api = AKShareFinanceAPI()
    df = ak_api.get_income_statement("600519")
"""

import akshare as ak
import pandas as pd
from typing import Optional


class AKShareFinanceAPI:
    """
    AKShare 免费财务数据 API
    文档: https://www.akshare.xyz/
    
    特点: 完全免费，无需注册，数据来自东方财富等公开渠道
    """
    
    def __init__(self):
        """初始化（无需Token）"""
        print("✅ AKShare API 初始化完成（免费数据源）")
    
    def get_stock_basic(self, ts_code: str) -> pd.DataFrame:
        """
        获取股票基本信息
        
        Args:
            ts_code: 股票代码，如 '600519.SH'
        
        Returns:
            股票基本信息DataFrame
        """
        try:
            # 转换代码格式
            code = ts_code.split('.')[0]
            
            # 获取所有股票列表
            df = ak.stock_info_a_code_name()
            
            # 查找指定股票
            stock = df[df['code'] == code]
            
            if stock.empty:
                return pd.DataFrame()
            
            # 格式化输出
            result = pd.DataFrame([{
                'ts_code': ts_code,
                'name': stock.iloc[0]['name'],
                'code': code
            }])
            
            return result
            
        except Exception as e:
            print(f"❌ 获取股票基本信息失败: {e}")
            return pd.DataFrame()
    
    def get_income_statement(self, ts_code: str, 
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取利润表（免费）
        
        Args:
            ts_code: 股票代码，如 '600519.SH'
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
        
        Returns:
            利润表DataFrame
        """
        try:
            # 转换代码格式
            code = ts_code.split('.')[0]
            
            print(f"📊 正在获取 {code} 利润表数据...")
            
            # 使用AKShare获取利润表（东方财富源）
            df = ak.stock_financial_report_sina(stock=code, symbol="利润表")
            
            if df.empty:
                print(f"⚠️ 未找到 {code} 的利润表数据")
                return df
            
            # 数据清洗和格式化
            df = self._clean_financial_data(df)
            
            print(f"✅ 成功获取 {code} 利润表，共 {len(df)} 期")
            return df
            
        except Exception as e:
            print(f"❌ 获取利润表失败: {e}")
            return pd.DataFrame()
    
    def get_balance_sheet(self, ts_code: str) -> pd.DataFrame:
        """
        获取资产负债表（免费）
        
        Args:
            ts_code: 股票代码
        
        Returns:
            资产负债表DataFrame
        """
        try:
            code = ts_code.split('.')[0]
            
            print(f"📊 正在获取 {code} 资产负债表...")
            
            df = ak.stock_financial_report_sina(stock=code, symbol="资产负债表")
            
            if df.empty:
                return df
            
            df = self._clean_financial_data(df)
            
            print(f"✅ 成功获取 {code} 资产负债表，共 {len(df)} 期")
            return df
            
        except Exception as e:
            print(f"❌ 获取资产负债表失败: {e}")
            return pd.DataFrame()
    
    def get_cash_flow(self, ts_code: str) -> pd.DataFrame:
        """
        获取现金流量表（免费）
        
        Args:
            ts_code: 股票代码
        
        Returns:
            现金流量表DataFrame
        """
        try:
            code = ts_code.split('.')[0]
            
            print(f"📊 正在获取 {code} 现金流量表...")
            
            df = ak.stock_financial_report_sina(stock=code, symbol="现金流量表")
            
            if df.empty:
                return df
            
            df = self._clean_financial_data(df)
            
            print(f"✅ 成功获取 {code} 现金流量表，共 {len(df)} 期")
            return df
            
        except Exception as e:
            print(f"❌ 获取现金流量表失败: {e}")
            return pd.DataFrame()
    
    def _clean_financial_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗财务数据并统一列名"""
        try:
            # 删除空行
            df = df.dropna(how='all')
            
            # 重置索引
            df = df.reset_index(drop=True)
            
            # 转换日期格式
            if '报告日' in df.columns:
                df['end_date'] = pd.to_datetime(df['报告日']).dt.strftime('%Y%m%d')
            elif '报告期' in df.columns:
                df['end_date'] = pd.to_datetime(df['报告期']).dt.strftime('%Y%m%d')
            
            # 过滤掉过早期数据（2010年前数据质量较差）
            if 'end_date' in df.columns:
                df['year'] = pd.to_datetime(df['end_date']).dt.year
                df = df[df['year'] >= 2010].copy()
                df = df.drop('year', axis=1)
            
            # 列名映射：中文 -> 英文（兼容Tushare格式）
            column_mapping = {
                '营业总收入': 'total_revenue',
                '营业收入': 'operate_revenue',
                '营业成本': 'operate_cost',
                '营业利润': 'operate_profit',
                '利润总额': 'total_profit',
                '净利润': 'n_income',
                '归属于母公司所有者的净利润': 'n_income_attr_p',
                '基本每股收益': 'basic_eps',
                '稀释每股收益': 'diluted_eps',
                '销售费用': 'sell_exp',
                '管理费用': 'admin_exp',
                '财务费用': 'fin_exp',
                '研发费用': 'rd_exp',
                '所得税费用': 'income_tax',
                '投资收益': 'invest_income',
                '资产减值损失': 'assets_impair_loss',
                '信用减值损失': 'credit_impair_loss',
                '其他收益': 'other_income',
                '资产处置收益': 'asset_disp_profit',
                '营业外收入': 'non_oper_income',
                '营业外支出': 'non_oper_exp',
                '营业税金及附加': 'operate_tax_add',
                '少数股东损益': 'minority_gain',
                '其他综合收益': 'other_compre_income',
                '综合收益总额': 'total_compre_income',
            }
            
            # 重命名列
            for cn, en in column_mapping.items():
                if cn in df.columns:
                    df[en] = df[cn]
            
            # 尝试转换数值列
            for col in df.columns:
                if col not in ['报告日', '报告期', 'end_date', '公告日期', '币种', '类型', '数据源', '是否审计', '更新日期']:
                    try:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    except:
                        pass
            
            # 按日期排序
            if 'end_date' in df.columns:
                df = df.sort_values('end_date').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            print(f"⚠️ 数据清洗警告: {e}")
            import traceback
            traceback.print_exc()
            return df
    
    def get_daily_price(self, ts_code: str, 
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取日线行情（免费）
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
        
        Returns:
            日线数据DataFrame
        """
        try:
            code = ts_code.split('.')[0]
            
            print(f"📈 正在获取 {code} 日线数据...")
            
            # 使用AKShare获取历史行情
            df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                   start_date=start_date, end_date=end_date, adjust="")
            
            if df.empty:
                return df
            
            # 格式化列名以兼容Tushare
            df = df.rename(columns={
                '日期': 'trade_date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'vol',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'pct_chg',
                '涨跌额': 'change',
                '换手率': 'turnover'
            })
            
            # 转换日期格式
            df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y%m%d')
            
            # 按日期排序
            df = df.sort_values('trade_date').reset_index(drop=True)
            
            # 计算均线
            if len(df) > 0:
                df['ma20'] = df['close'].rolling(window=20, min_periods=1).mean()
                df['ma60'] = df['close'].rolling(window=60, min_periods=1).mean()
                df['daily_return'] = df['close'].pct_change()
            
            print(f"✅ 成功获取 {code} 日线数据，共 {len(df)} 条")
            return df
            
        except Exception as e:
            print(f"❌ 获取日线数据失败: {e}")
            return pd.DataFrame()
    
    def get_financial_summary(self, ts_code: str) -> dict:
        """
        获取财务摘要（核心指标）
        
        Args:
            ts_code: 股票代码
        
        Returns:
            财务指标字典
        """
        try:
            code = ts_code.split('.')[0]
            
            # 获取主要财务指标
            df = ak.stock_financial_analysis_indicator(symbol=code)
            
            if df.empty:
                return {}
            
            # 取最新一期数据
            latest = df.iloc[0]
            
            summary = {
                'roe': latest.get('净资产收益率'),
                'gross_margin': latest.get('销售毛利率'),
                'net_margin': latest.get('销售净利率'),
                'debt_ratio': latest.get('资产负债率'),
                'eps': latest.get('基本每股收益'),
                'revenue_growth': latest.get('营业收入增长率'),
                'profit_growth': latest.get('净利润增长率')
            }
            
            return summary
            
        except Exception as e:
            print(f"❌ 获取财务摘要失败: {e}")
            return {}


# 测试代码
if __name__ == "__main__":
    api = AKShareFinanceAPI()
    
    # 测试获取利润表
    print("\n=== 测试获取茅台利润表 ===")
    income = api.get_income_statement("600519.SH")
    if not income.empty:
        print(f"获取到 {len(income)} 行数据")
        print(income.head())
    
    # 测试获取日线
    print("\n=== 测试获取茅台日线 ===")
    price = api.get_daily_price("600519.SH", "20241201", "20241231")
    if not price.empty:
        print(f"获取到 {len(price)} 行数据")
        print(price[['trade_date', 'open', 'close', 'ma20']].tail())
