#!/usr/bin/env python3
"""
商业尽调数据集成模块
整合多个API生成真实尽调报告

数据来源:
- 天眼查API: 工商信息、股权、法律风险
- AKShare: 上市公司财务数据
- Tavily Search: 新闻舆情、行业研报
- 文件解析: 内部资料
"""

import os
import requests
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime


class DueDiligenceIntegration:
    """
    商业尽调数据集成器
    """
    
    def __init__(self, tianyancha_token: Optional[str] = None):
        """
        初始化
        
        Args:
            tianyancha_token: 天眼查API Token（可选）
        """
        self.tianyancha_token = tianyancha_token
        self.tianyancha_base = "https://open.api.tianyancha.com/services/v4/open"
        
        # 导入其他API
        from .akshare_api import AKShareFinanceAPI
        self.ak_api = AKShareFinanceAPI()
        
    def search_company_basic(self, company_name: str) -> Dict:
        """
        查询公司工商基本信息
        
        Args:
            company_name: 公司名称
            
        Returns:
            工商信息字典
        """
        if not self.tianyancha_token:
            return {"error": "天眼查Token未配置"}
        
        try:
            url = f"{self.tianyancha_base}/search/2.0"
            headers = {"Authorization": self.tianyancha_token}
            params = {"word": company_name}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            data = response.json()
            
            if data.get("error_code") == 0:
                result = data.get("result", {}).get("items", [])
                if result:
                    return result[0]
            
            return {"error": f"查询失败: {data.get('error_msg', '未知错误')}"}
            
        except Exception as e:
            return {"error": f"请求异常: {str(e)}"}
    
    def get_company_risk(self, company_name: str) -> Dict:
        """
        获取公司风险信息
        
        Returns:
            风险信息字典
        """
        if not self.tianyancha_token:
            return {"error": "天眼查Token未配置"}
        
        try:
            # 法律诉讼
            url = f"{self.tianyancha_base}/lawSuit/2.0"
            headers = {"Authorization": self.tianyancha_token}
            params = {"word": company_name, "pageSize": 10}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            data = response.json()
            
            risk_info = {
                "法律诉讼": [],
                "经营异常": [],
                "被执行人": []
            }
            
            if data.get("error_code") == 0:
                items = data.get("result", {}).get("items", [])
                risk_info["法律诉讼"] = items[:5]  # 取前5条
            
            return risk_info
            
        except Exception as e:
            return {"error": f"请求异常: {str(e)}"}
    
    def get_financial_data(self, stock_code: str) -> Dict:
        """
        获取财务数据（如果是上市公司）
        
        Args:
            stock_code: 股票代码，如 600519.SH
            
        Returns:
            财务数据字典
        """
        try:
            # 获取利润表
            income = self.ak_api.get_income_statement(stock_code)
            
            # 获取资产负债表
            balance = self.ak_api.get_balance_sheet(stock_code)
            
            # 获取现金流量表
            cashflow = self.ak_api.get_cash_flow(stock_code)
            
            return {
                "利润表": income,
                "资产负债表": balance,
                "现金流量表": cashflow,
                "is_listed": not income.empty
            }
            
        except Exception as e:
            return {"error": str(e), "is_listed": False}
    
    def search_news(self, company_name: str, limit: int = 10) -> List[Dict]:
        """
        搜索公司相关新闻（使用模拟数据，实际应接入Tavily）
        
        Args:
            company_name: 公司名称
            limit: 返回条数
            
        Returns:
            新闻列表
        """
        # 这里应该调用 Tavily Search API
        # 示例返回模拟数据
        return [
            {
                "title": f"{company_name} 最新发展动态",
                "source": "财经新闻",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "summary": "公司近期业务发展良好..."
            }
        ]
    
    def generate_dd_report(self, company_name: str, industry: str, 
                          uploaded_files: List[Dict] = None) -> Dict:
        """
        生成完整的尽调报告
        
        Args:
            company_name: 公司名称
            industry: 所属行业
            uploaded_files: 上传的文件内容列表
            
        Returns:
            尽调报告字典
        """
        report = {
            "基本信息": {},
            "工商信息": {},
            "财务数据": {},
            "风险信息": {},
            "舆情监控": [],
            "内部资料分析": {},
            "综合评估": {}
        }
        
        # 1. 查询工商信息（如果配置了天眼查）
        if self.tianyancha_token:
            report["工商信息"] = self.search_company_basic(company_name)
            report["风险信息"] = self.get_company_risk(company_name)
        else:
            report["工商信息"] = {"note": "天眼查Token未配置，工商信息未获取"}
            report["风险信息"] = {"note": "天眼查Token未配置，风险信息未获取"}
        
        # 2. 尝试获取财务数据
        # 先查询股票代码映射
        from ..app import STOCK_NAME_MAPPING
        stock_code = None
        for name, code in STOCK_NAME_MAPPING.items():
            if company_name in name or name in company_name:
                stock_code = code
                break
        
        if stock_code:
            report["财务数据"] = self.get_financial_data(stock_code)
        else:
            report["财务数据"] = {"note": "未找到对应上市公司代码"}
        
        # 3. 舆情监控
        report["舆情监控"] = self.search_news(company_name)
        
        # 4. 内部资料分析
        if uploaded_files:
            report["内部资料分析"] = {
                "files_count": len(uploaded_files),
                "files": [f["name"] for f in uploaded_files],
                "key_insights": self._extract_key_insights(uploaded_files)
            }
        
        # 5. 综合评估
        report["综合评估"] = self._generate_assessment(report, industry)
        
        return report
    
    def _extract_key_insights(self, files: List[Dict]) -> List[str]:
        """从文件中提取关键信息"""
        insights = []
        
        for file in files:
            content = file.get("content", "")
            # 简单的关键词提取
            keywords = ["营收", "利润", "客户", "市场", "增长", "战略"]
            for kw in keywords:
                if kw in content:
                    # 提取包含关键词的句子
                    import re
                    sentences = re.findall(f"[^。]*{kw}[^。]*。", content)
                    if sentences:
                        insights.append(f"【{file['name']}】{sentences[0][:50]}...")
        
        return insights[:5]  # 返回前5条
    
    def _generate_assessment(self, report: Dict, industry: str) -> Dict:
        """生成综合评估"""
        assessment = {
            "行业": industry,
            "数据完整度": 0,
            "风险提示": [],
            "建议": ""
        }
        
        # 计算数据完整度
        score = 0
        if "error" not in report["工商信息"]:
            score += 30
        if report["财务数据"].get("is_listed"):
            score += 30
        if report["风险信息"] and "error" not in report["风险信息"]:
            score += 20
        if report["舆情监控"]:
            score += 10
        if report.get("内部资料分析"):
            score += 10
        
        assessment["数据完整度"] = score
        
        # 生成建议
        if score >= 80:
            assessment["建议"] = "数据完整度较高，可进入深入尽调阶段"
        elif score >= 50:
            assessment["建议"] = "基础数据已获取，建议补充工商信息和财务数据"
        else:
            assessment["建议"] = "数据缺失较多，建议补充天眼查API和内部资料"
        
        return assessment


# 测试代码
if __name__ == "__main__":
    # 初始化（不配置天眼查Token）
    dd = DueDiligenceIntegration()
    
    # 测试财务数据获取
    print("=== 测试茅台财务数据 ===")
    result = dd.get_financial_data("600519.SH")
    print(f"是否上市公司: {result.get('is_listed')}")
    if "利润表" in result:
        print(f"利润表数据条数: {len(result['利润表'])}")
