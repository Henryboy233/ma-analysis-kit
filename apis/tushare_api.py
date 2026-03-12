#!/usr/bin/env python3
"""
Tushare API 对接模块
Tushare API Module for A-Share Financial Data

功能:
- A股财务数据获取（利润表、资产负债表、现金流量表）
- 估值指标查询（PE、PB、市值）
- 股票基础信息
- 可比公司分析数据

使用:
    from apis.tushare_api import TushareFinanceAPI
    
    ts_api = TushareFinanceAPI("your_token")
    df = ts_api.get_income_statement("600519.SH", "20230101", "20231231")
"""

import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional


class TushareFinanceAPI:
    """
    Tushare Pro API 封装
    文档: https://tushare.pro/document/2
    
    注意: 需要注册 Tushare 账号获取 Token
    大部分基础数据免费，部分高级数据需要积分
    """
    
    def __init__(self, token: str):
        """
        初始化
        
        Args:
            token: Tushare Pro API Token
        """
        self.token = token
        ts.set_token(token)
        self.pro = ts.pro_api()
    
    def get_stock_basic(self, ts_code: Optional[str] = None, 
                       name: Optional[str] = None,
                       exchange: Optional[str] = None) -> pd.DataFrame:
        """
        获取股票基础信息
        
        Args:
            ts_code: 股票代码，如 '600519.SH'
            name: 股票名称，如 '贵州茅台'
            exchange: 交易所，'SSE'上交所，'SZSE'深交所
            
        Returns:
            股票基础信息DataFrame
        """
        try:
            df = self.pro.stock_basic(
                ts_code=ts_code,
                name=name,
                exchange=exchange,
                fields='ts_code,symbol,name,area,industry,list_date'
            )
            return df
        except Exception as e:
            print(f"获取股票基础信息失败: {e}")
            return pd.DataFrame()
    
    def get_income_statement(self, ts_code: str, 
                            start_date: str, 
                            end_date: str) -> pd.DataFrame:
        """
        获取利润表（Income Statement）
        
        Args:
            ts_code: 股票代码，如 '600519.SH'
            start_date: 开始日期，格式 'YYYYMMDD'
            end_date: 结束日期，格式 'YYYYMMDD'
            
        Returns:
            利润表DataFrame
            包含: 营业收入、营业成本、净利润等核心指标
        """
        try:
            # 获取单季度数据
            df = self.pro.income(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                fields='ts_code,ann_date,end_date,total_revenue,total_cogs,'
                       'oper_exp,admin_exp,fin_exp,sell_exp,'
                       'operate_profit,n_income,netprofit_margin'
            )
            
            if df.empty:
                print(f"⚠️  未找到 {ts_code} 在 {start_date} 至 {end_date} 期间的利润表数据")
                return df
            
            # 按日期排序
            df = df.sort_values('end_date').reset_index(drop=True)
            
            # 添加计算字段
            if 'total_revenue' in df.columns and 'n_income' in df.columns:
                df['net_margin'] = (df['n_income'] / df['total_revenue'] * 100).round(2)
            
            print(f"✅ 成功获取 {ts_code} 利润表，共 {len(df)} 期")
            return df
            
        except Exception as e:
            print(f"❌ 获取利润表失败: {e}")
            return pd.DataFrame()
    
    def get_balance_sheet(self, ts_code: str,
                         start_date: str,
                         end_date: str) -> pd.DataFrame:
        """
        获取资产负债表（Balance Sheet）
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期 'YYYYMMDD'
            end_date: 结束日期 'YYYYMMDD'
            
        Returns:
            资产负债表DataFrame
            包含: 总资产、负债、股东权益等
        """
        try:
            df = self.pro.balancesheet(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                fields='ts_code,ann_date,end_date,total_assets,total_liab,'
                       'total_hldr_eqy_exc_min_int,total_liab_hldr_eqy'
            )
            
            if df.empty:
                print(f"⚠️  未找到资产负债表数据")
                return df
            
            df = df.sort_values('end_date').reset_index(drop=True)
            
            # 计算资产负债率
            if 'total_liab' in df.columns and 'total_assets' in df.columns:
                df['debt_ratio'] = (df['total_liab'] / df['total_assets'] * 100).round(2)
            
            print(f"✅ 成功获取 {ts_code} 资产负债表，共 {len(df)} 期")
            return df
            
        except Exception as e:
            print(f"❌ 获取资产负债表失败: {e}")
            return pd.DataFrame()
    
    def get_daily_price(self, ts_code: str,
                       start_date: str,
                       end_date: str) -> pd.DataFrame:
        """
        获取日线行情（Price Data）
        最低积分要求: 120
        
        Args:
            ts_code: 股票代码，如 '600519.SH'
            start_date: 开始日期 'YYYYMMDD'
            end_date: 结束日期 'YYYYMMDD'
            
        Returns:
            日线数据DataFrame
            包含: 开盘、收盘、最高、最低、成交量等
        """
        try:
            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
            
            if df.empty:
                print(f"⚠️  未找到 {ts_code} 在 {start_date} 至 {end_date} 期间的日线数据")
                return df
            
            # 按日期排序
            df = df.sort_values('trade_date').reset_index(drop=True)
            
            # 计算技术指标
            if len(df) > 0:
                # 20日均线
                df['ma20'] = df['close'].rolling(window=20).mean()
                # 60日均线
                df['ma60'] = df['close'].rolling(window=60).mean()
                # 日收益率
                df['daily_return'] = df['close'].pct_change()
                # 波动率（20日）
                df['volatility_20'] = df['daily_return'].rolling(window=20).std() * 100
            
            print(f"✅ 成功获取 {ts_code} 日线数据，共 {len(df)} 条")
            return df
            
        except Exception as e:
            print(f"❌ 获取日线数据失败: {e}")
            return pd.DataFrame()
    
    def get_cash_flow(self, ts_code: str,
                     start_date: str,
                     end_date: str) -> pd.DataFrame:
        """
        获取现金流量表（Cash Flow Statement）
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            现金流量表DataFrame
            包含: 经营、投资、筹资活动现金流
        """
        try:
            df = self.pro.cashflow(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                fields='ts_code,ann_date,end_date,n_cashflow_act,'
                       'n_cashflow_inv_act,n_cashflow_fin_act,'
                       'free_cashflow'
            )
            
            if df.empty:
                print(f"⚠️  未找到现金流量表数据")
                return df
            
            df = df.sort_values('end_date').reset_index(drop=True)
            print(f"✅ 成功获取 {ts_code} 现金流量表，共 {len(df)} 期")
            return df
            
        except Exception as e:
            print(f"❌ 获取现金流量表失败: {e}")
            return pd.DataFrame()
    
    def get_valuation_metrics(self, ts_code: str,
                             trade_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取每日估值指标（PE、PB、市值等）
        
        Args:
            ts_code: 股票代码
            trade_date: 交易日期 'YYYYMMDD'，默认为最近交易日
            
        Returns:
            估值指标DataFrame
            包含: 收盘价、PE、PB、总市值等
        """
        try:
            # 如果没有指定日期，获取最近一天的数据
            if not trade_date:
                today = datetime.now()
                # 获取最近交易日（简单处理，实际需要排除节假日）
                if today.weekday() >= 5:  # 周六或周日
                    today = today - timedelta(days=today.weekday() - 4)
                trade_date = today.strftime('%Y%m%d')
            
            df = self.pro.daily_basic(
                ts_code=ts_code,
                trade_date=trade_date,
                fields='ts_code,trade_date,close,turnover_rate,'
                       'pe,pe_ttm,pb,ps,total_mv,circ_mv'
            )
            
            if df.empty:
                print(f"⚠️  未找到 {ts_code} 在 {trade_date} 的估值数据")
                return df
            
            print(f"✅ 成功获取 {ts_code} 估值指标")
            return df
            
        except Exception as e:
            print(f"❌ 获取估值指标失败: {e}")
            return pd.DataFrame()
    
    def get_company_intro(self, ts_code: str) -> pd.DataFrame:
        """
        获取上市公司简介
        
        Args:
            ts_code: 股票代码
            
        Returns:
            公司简介DataFrame
            包含: 主营业务、经营范围、公司简介等
        """
        try:
            df = self.pro.stock_company(
                ts_code=ts_code,
                fields='ts_code,exchange,chairman,manager,'
                       'reg_capital,main_business,business_scope,introduction'
            )
            
            if not df.empty:
                print(f"✅ 成功获取 {ts_code} 公司简介")
            return df
            
        except Exception as e:
            print(f"❌ 获取公司简介失败: {e}")
            return pd.DataFrame()
    
    def get_top10_holders(self, ts_code: str, 
                         end_date: str) -> pd.DataFrame:
        """
        获取前十大股东
        
        Args:
            ts_code: 股票代码
            end_date: 报告期 'YYYYMMDD'
            
        Returns:
            前十大股东DataFrame
        """
        try:
            df = self.pro.top10_holders(
                ts_code=ts_code,
                end_date=end_date
            )
            
            if not df.empty:
                print(f"✅ 成功获取 {ts_code} 前十大股东")
            return df
            
        except Exception as e:
            print(f"❌ 获取前十大股东失败: {e}")
            return pd.DataFrame()
    
    def get_fund_holdings(self, ts_code: str,
                         end_date: str) -> pd.DataFrame:
        """
        获取机构持股（基金持股）
        
        Args:
            ts_code: 股票代码
            end_date: 报告期 'YYYYMMDD'
            
        Returns:
            机构持股DataFrame
        """
        try:
            df = self.pro.fund_holdings(
                ts_code=ts_code,
                end_date=end_date
            )
            
            if not df.empty:
                print(f"✅ 成功获取 {ts_code} 机构持股")
            return df
            
        except Exception as e:
            print(f"❌ 获取机构持股失败: {e}")
            return pd.DataFrame()
    
    def get_industry_peers(self, industry: str) -> pd.DataFrame:
        """
        获取同行业公司列表（用于可比公司分析）
        
        Args:
            industry: 行业分类，如 '医药生物'
            
        Returns:
            同行业公司列表
        """
        try:
            df = self.pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,area,industry,list_date'
            )
            
            # 筛选行业
            peers = df[df['industry'] == industry]
            
            print(f"✅ 找到 {len(peers)} 家同行业公司")
            return peers
            
        except Exception as e:
            print(f"❌ 获取同行业公司失败: {e}")
            return pd.DataFrame()
    
    def get_full_financials(self, ts_code: str,
                           start_date: str,
                           end_date: str) -> dict:
        """
        获取完整财务数据（三表合一）
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            包含三表数据的字典
        """
        print(f"\n📊 开始获取 {ts_code} 完整财务数据...\n")
        
        result = {
            'ts_code': ts_code,
            'collection_time': datetime.now().isoformat(),
            'income_statement': self.get_income_statement(ts_code, start_date, end_date),
            'balance_sheet': self.get_balance_sheet(ts_code, start_date, end_date),
            'cash_flow': self.get_cash_flow(ts_code, start_date, end_date),
            'valuation': self.get_valuation_metrics(ts_code),
            'company_intro': self.get_company_intro(ts_code)
        }
        
        print(f"\n✅ 财务数据获取完成！")
        return result
    
    def calculate_financial_ratios(self, income_df: pd.DataFrame,
                                   balance_df: pd.DataFrame) -> pd.DataFrame:
        """
        计算财务比率
        
        Args:
            income_df: 利润表DataFrame
            balance_df: 资产负债表DataFrame
            
        Returns:
            财务比率DataFrame
        """
        ratios = pd.DataFrame()
        
        if not income_df.empty:
            # 盈利能力指标
            if 'total_revenue' in income_df.columns and 'n_income' in income_df.columns:
                ratios['net_margin'] = (income_df['n_income'] / income_df['total_revenue'] * 100).round(2)
            
            if 'total_revenue' in income_df.columns and 'total_cogs' in income_df.columns:
                ratios['gross_margin'] = ((income_df['total_revenue'] - income_df['total_cogs']) 
                                         / income_df['total_revenue'] * 100).round(2)
        
        if not balance_df.empty:
            # 偿债能力指标
            if 'total_liab' in balance_df.columns and 'total_assets' in balance_df.columns:
                ratios['debt_ratio'] = (balance_df['total_liab'] / balance_df['total_assets'] * 100).round(2)
        
        return ratios


# ================= 使用示例 =================
if __name__ == "__main__":
    import os
    
    # 从环境变量读取Token
    TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN", "your_token_here")
    
    if TUSHARE_TOKEN == "your_token_here":
        print("⚠️  请先设置 Tushare API Token:")
        print("   1. 访问 https://tushare.pro/register 注册账号")
        print("   2. 获取 Token")
        print("   3. export TUSHARE_TOKEN='your_token'")
        exit(1)
    
    # 初始化API
    ts_api = TushareFinanceAPI(TUSHARE_TOKEN)
    
    # 测试：贵州茅台
    target_code = "600519.SH"  # 贵州茅台
    target_name = "贵州茅台"
    
    print("=" * 70)
    print("Tushare API 测试 - A股财务数据获取")
    print("=" * 70)
    
    # 1. 获取股票基础信息
    print(f"\n📋 1. 股票基础信息:")
    basic = ts_api.get_stock_basic(ts_code=target_code)
    if not basic.empty:
        print(f"   股票代码: {basic.iloc[0]['ts_code']}")
        print(f"   股票名称: {basic.iloc[0]['name']}")
        print(f"   所属行业: {basic.iloc[0]['industry']}")
        print(f"   上市日期: {basic.iloc[0]['list_date']}")
    
    # 2. 获取利润表
    print(f"\n📊 2. 利润表 (最近4个季度):")
    income = ts_api.get_income_statement(target_code, '20230101', '20241231')
    if not income.empty:
        # 显示关键列
        display_cols = ['end_date', 'total_revenue', 'n_income', 'net_margin']
        available_cols = [c for c in display_cols if c in income.columns]
        print(income[available_cols].tail(4).to_string(index=False))
    
    # 3. 获取估值指标
    print(f"\n💰 3. 最新估值指标:")
    valuation = ts_api.get_valuation_metrics(target_code)
    if not valuation.empty:
        print(f"   收盘价: {valuation.iloc[0]['close']}")
        print(f"   市盈率(PE): {valuation.iloc[0]['pe']}")
        print(f"   市盈率(TTM): {valuation.iloc[0]['pe_ttm']}")
        print(f"   市净率(PB): {valuation.iloc[0]['pb']}")
        print(f"   总市值: {valuation.iloc[0]['total_mv']} 万元")
    
    # 4. 获取同行业公司
    print(f"\n🏭 4. 同行业可比公司:")
    if not basic.empty:
        industry = basic.iloc[0]['industry']
        peers = ts_api.get_industry_peers(industry)
        if not peers.empty:
            print(f"   行业: {industry}")
            print(f"   前5家: {', '.join(peers['name'].head(5).tolist())}")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)
