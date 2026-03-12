#!/usr/bin/env python3
"""
API 统一管理器
API Manager

统一管理天眼查、Tushare等多个数据源的API调用
提供统一的接口和错误处理

使用:
    from apis.api_manager import APIManager
    
    manager = APIManager()
    result = manager.full_analysis("600519.SH", "贵州茅台")
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional
import pandas as pd

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from apis.tianyancha_api import TianyanchaAPI
from apis.tushare_api import TushareFinanceAPI


class APIManager:
    """
    API 统一管理器
    
    自动从环境变量或配置文件加载Token
    提供统一的数据获取接口
    """
    
    def __init__(self, 
                 tyc_token: Optional[str] = None,
                 ts_token: Optional[str] = None):
        """
        初始化API管理器
        
        Args:
            tyc_token: 天眼查Token，默认从环境变量 TIANYANCHA_TOKEN 读取
            ts_token: Tushare Token，默认从环境变量 TUSHARE_TOKEN 读取
        """
        # 天眼查
        self.tyc_token = tyc_token or os.getenv("TIANYANCHA_TOKEN")
        self.tyc_api = None
        if self.tyc_token:
            self.tyc_api = TianyanchaAPI(self.tyc_token)
        else:
            print("⚠️  未配置天眼查Token，工商信息功能不可用")
        
        # Tushare
        self.ts_token = ts_token or os.getenv("TUSHARE_TOKEN")
        self.ts_api = None
        if self.ts_token:
            self.ts_api = TushareFinanceAPI(self.ts_token)
        else:
            print("⚠️  未配置Tushare Token，A股财务数据功能不可用")
    
    def is_tyc_available(self) -> bool:
        """检查天眼查API是否可用"""
        return self.tyc_api is not None
    
    def is_ts_available(self) -> bool:
        """检查Tushare API是否可用"""
        return self.ts_api is not None
    
    def get_company_basic_info(self, company_name: str) -> Dict:
        """
        获取公司基本信息（优先使用天眼查）
        
        Args:
            company_name: 公司全称
            
        Returns:
            公司基本信息字典
        """
        if not self.is_tyc_available():
            return {"error": "天眼查API未配置"}
        
        return self.tyc_api.get_base_info_v4(company_name)
    
    def get_company_risk_info(self, company_name: str) -> Dict:
        """
        获取公司风险信息
        
        Args:
            company_name: 公司全称
            
        Returns:
            风险信息字典
        """
        if not self.is_tyc_available():
            return {"error": "天眼查API未配置"}
        
        risks = {
            "lawsuits": self.tyc_api.get_lawsuits(company_name),
            "executed": self.tyc_api.get_executed_persons(company_name),
            "abnormal": self.tyc_api.get_abnormal_info(company_name),
            "penalty": self.tyc_api.get_administrative_penalty(company_name)
        }
        return risks
    
    def get_financial_data(self, ts_code: str, 
                          start_date: str, 
                          end_date: str) -> Dict:
        """
        获取财务数据（使用Tushare）
        
        Args:
            ts_code: 股票代码，如 '600519.SH'
            start_date: 开始日期 'YYYYMMDD'
            end_date: 结束日期 'YYYYMMDD'
            
        Returns:
            财务数据字典
        """
        if not self.is_ts_available():
            return {"error": "Tushare API未配置"}
        
        return self.ts_api.get_full_financials(ts_code, start_date, end_date)
    
    def get_valuation(self, ts_code: str) -> pd.DataFrame:
        """
        获取估值指标
        
        Args:
            ts_code: 股票代码
            
        Returns:
            估值指标DataFrame
        """
        if not self.is_ts_available():
            return pd.DataFrame()
        
        return self.ts_api.get_valuation_metrics(ts_code)
    
    def get_comparable_companies(self, ts_code: str) -> pd.DataFrame:
        """
        获取可比公司列表
        
        Args:
            ts_code: 股票代码
            
        Returns:
            同行业公司DataFrame
        """
        if not self.is_ts_available():
            return pd.DataFrame()
        
        # 先获取公司行业
        basic = self.ts_api.get_stock_basic(ts_code=ts_code)
        if basic.empty:
            return pd.DataFrame()
        
        industry = basic.iloc[0]['industry']
        return self.ts_api.get_industry_peers(industry)
    
    def full_analysis(self, ts_code: str, company_name: str) -> Dict:
        """
        完整分析 - 整合工商+财务+估值数据
        
        Args:
            ts_code: 股票代码 (A股上市公司)
            company_name: 公司全称
            
        Returns:
            完整分析数据字典
        """
        print("\n" + "=" * 70)
        print(f"开始完整分析: {company_name} ({ts_code})")
        print("=" * 70 + "\n")
        
        result = {
            "company_name": company_name,
            "ts_code": ts_code,
            "analysis_time": pd.Timestamp.now().isoformat(),
            "basic_info": {},
            "risk_info": {},
            "financial_data": {},
            "valuation": {},
            "peers": {}
        }
        
        # 1. 工商信息
        if self.is_tyc_available():
            print("📋 获取工商信息...")
            result["basic_info"] = self.get_company_basic_info(company_name)
            result["risk_info"] = self.get_company_risk_info(company_name)
        else:
            print("⚠️  跳过工商信息（未配置天眼查）")
        
        # 2. 财务数据
        if self.is_ts_available():
            print("\n📊 获取财务数据...")
            end_date = pd.Timestamp.now()
            start_date = end_date - pd.DateOffset(years=2)
            result["financial_data"] = self.get_financial_data(
                ts_code,
                start_date.strftime('%Y%m%d'),
                end_date.strftime('%Y%m%d')
            )
            
            # 3. 估值
            print("\n💰 获取估值指标...")
            result["valuation"] = self.get_valuation(ts_code)
            
            # 4. 可比公司
            print("\n🏭 获取可比公司...")
            result["peers"] = self.get_comparable_companies(ts_code)
        else:
            print("⚠️  跳过财务数据（未配置Tushare）")
        
        print("\n" + "=" * 70)
        print("✅ 分析完成!")
        print("=" * 70 + "\n")
        
        return result
    
    def generate_report_summary(self, analysis_result: Dict) -> str:
        """
        生成报告摘要
        
        Args:
            analysis_result: full_analysis的返回结果
            
        Returns:
            Markdown格式的报告摘要
        """
        company = analysis_result.get("company_name", "未知")
        
        lines = [
            f"# {company} 分析报告摘要",
            "",
            f"**分析时间**: {analysis_result.get('analysis_time', 'N/A')}",
            "",
            "## 1. 基本信息",
            ""
        ]
        
        # 工商信息
        basic = analysis_result.get("basic_info", {})
        if basic:
            lines.extend([
                f"- **法人代表**: {basic.get('legalPersonName', 'N/A')}",
                f"- **注册资本**: {basic.get('regCapital', 'N/A')}",
                f"- **成立日期**: {basic.get('estiblishTime', 'N/A')}",
                f"- **经营状态**: {basic.get('regStatus', 'N/A')}",
                ""
            ])
        
        # 财务摘要
        lines.extend(["## 2. 财务摘要", ""])
        fin = analysis_result.get("financial_data", {})
        income = fin.get("income_statement")
        if income is not None and not income.empty:
            latest = income.iloc[-1]
            lines.extend([
                f"- **最近报告期**: {latest.get('end_date', 'N/A')}",
                f"- **营业收入**: {latest.get('total_revenue', 'N/A')} 万元",
                f"- **净利润**: {latest.get('n_income', 'N/A')} 万元",
                ""
            ])
        
        # 估值
        lines.extend(["## 3. 估值指标", ""])
        val = analysis_result.get("valuation")
        if val is not None and not val.empty:
            v = val.iloc[0]
            lines.extend([
                f"- **市盈率(PE)**: {v.get('pe', 'N/A')}",
                f"- **市净率(PB)**: {v.get('pb', 'N/A')}",
                f"- **总市值**: {v.get('total_mv', 'N/A')} 万元",
                ""
            ])
        
        lines.extend(["---", "", "*报告由MA Analysis Kit自动生成*"])
        
        return "\n".join(lines)


# ================= 使用示例 =================
if __name__ == "__main__":
    # 初始化管理器（自动从环境变量读取Token）
    manager = APIManager()
    
    # 检查可用性
    print("\nAPI 状态检查:")
    print(f"  天眼查: {'✅ 可用' if manager.is_tyc_available() else '❌ 未配置'}")
    print(f"  Tushare: {'✅ 可用' if manager.is_ts_available() else '❌ 未配置'}")
    
    # 如果都配置了，运行完整分析
    if manager.is_tyc_available() and manager.is_ts_available():
        print("\n开始完整分析示例...\n")
        
        # 分析贵州茅台
        result = manager.full_analysis(
            ts_code="600519.SH",
            company_name="贵州茅台酒股份有限公司"
        )
        
        # 生成摘要
        summary = manager.generate_report_summary(result)
        print(summary)
        
        # 保存到文件
        with open("analysis_summary.md", "w", encoding="utf-8") as f:
            f.write(summary)
        print("\n报告已保存到: analysis_summary.md")
    else:
        print("\n⚠️  请配置API Token后运行完整分析")
        print("   export TIANYANCHA_TOKEN='your_token'")
        print("   export TUSHARE_TOKEN='your_token'")
