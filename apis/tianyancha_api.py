#!/usr/bin/env python3
"""
天眼查 API 对接模块
Tianyancha API Module

功能:
- 企业基本信息查询
- 股东信息/股权穿透
- 法律诉讼/风险信息
- 工商变更记录

使用:
    from apis.tianyancha_api import TianyanchaAPI
    
    tyc = TianyanchaAPI("your_token")
    info = tyc.get_base_info("北京月之暗面科技有限公司")
"""

import requests
import json
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional


class TianyanchaAPI:
    """
    天眼查开放平台 API 封装
    文档: https://open.tianyancha.com/
    """
    
    def __init__(self, api_token: str):
        """
        初始化
        
        Args:
            api_token: 天眼查开放平台授权Token
        """
        self.api_token = api_token
        self.headers = {'Authorization': api_token}
        # 新版API地址
        self.base_url_v4 = "https://open.api.tianyancha.com/services/open"
        # 旧版API地址
        self.base_url_v3 = "https://open.api.tianyancha.com/services/v3/open"
    
    def _make_request(self, url: str, params: dict) -> dict:
        """
        发送HTTP请求
        
        Args:
            url: API地址
            params: 请求参数
            
        Returns:
            API响应结果
        """
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error_code": -1, "reason": f"请求异常: {str(e)}"}
        except json.JSONDecodeError:
            return {"error_code": -1, "reason": "JSON解析失败"}
    
    def search_company(self, keyword: str) -> dict:
        """
        企业搜索
        
        Args:
            keyword: 公司名称/关键词
            
        Returns:
            搜索结果，包含公司列表
        """
        url = f"{self.base_url_v3}/search/solrV2"
        params = {'key': keyword}
        
        data = self._make_request(url, params)
        
        if data.get('error_code') == 0:
            print(f"✅ 成功搜索 '{keyword}'，找到 {data.get('result', {}).get('total', 0)} 条结果")
        else:
            print(f"❌ 搜索失败: {data.get('reason')}")
        
        return data
    
    def get_base_info_v4(self, keyword: str) -> dict:
        """
        获取企业基本工商信息 (v4版本，推荐)
        
        Args:
            keyword: 公司全称或统一信用代码
            
        Returns:
            企业基本信息
        """
        url = f"{self.base_url_v4}/ic/baseinfo/2.0"
        params = {'keyword': keyword}
        
        data = self._make_request(url, params)
        
        if data.get('error_code') == 0:
            print(f"✅ 成功获取 '{keyword}' 基本信息")
            return data.get('result', {})
        else:
            print(f"❌ 获取失败: {data.get('reason')}")
            return None
    
    def get_base_info_v3(self, name: str) -> dict:
        """
        获取企业基本信息 (v3版本)
        
        Args:
            name: 公司全称
            
        Returns:
            企业基本信息
        """
        url = f"{self.base_url_v3}/baseinfo.json"
        params = {'name': urllib.parse.quote(name)}
        
        data = self._make_request(url, params)
        
        if data.get('error_code') == 0:
            print(f"✅ 成功获取 '{name}' 基本信息")
            return data.get('result', {})
        else:
            print(f"❌ 获取失败: {data.get('reason')}")
            return None
    
    def get_shareholders(self, keyword: str) -> List[dict]:
        """
        获取企业股东信息（用于股权穿透）
        
        Args:
            keyword: 公司全称或统一信用代码
            
        Returns:
            股东信息列表
        """
        url = f"{self.base_url_v4}/ic/shareholder/2.0"
        params = {'keyword': keyword}
        
        data = self._make_request(url, params)
        
        if data.get('error_code') == 0:
            items = data.get('result', {}).get('items', [])
            print(f"✅ 成功获取股东信息，共 {len(items)} 位股东")
            return items
        else:
            print(f"❌ 获取股东信息失败: {data.get('reason')}")
            return []
    
    def get_equity_structure(self, company_id: str) -> dict:
        """
        获取股权结构图（穿透图）
        
        Args:
            company_id: 天眼查公司ID
            
        Returns:
            股权结构数据
        """
        url = f"{self.base_url_v3}/equityRatio.json"
        params = {'id': company_id}
        
        data = self._make_request(url, params)
        
        if data.get('error_code') == 0:
            print(f"✅ 成功获取股权结构图")
            return data.get('result', {})
        else:
            print(f"❌ 获取股权结构失败: {data.get('reason')}")
            return None
    
    def get_lawsuits(self, name: str, page: int = 1) -> dict:
        """
        获取法律诉讼信息
        
        Args:
            name: 公司全称
            page: 页码，默认第1页
            
        Returns:
            法律诉讼列表
        """
        url = f"{self.base_url_v3}/lawsuit.json"
        params = {
            'name': urllib.parse.quote(name),
            'pageNum': page
        }
        
        data = self._make_request(url, params)
        
        if data.get('error_code') == 0:
            total = data.get('result', {}).get('total', 0)
            print(f"✅ 成功获取法律诉讼，共 {total} 条")
            return data.get('result', {})
        else:
            print(f"❌ 获取法律诉讼失败: {data.get('reason')}")
            return None
    
    def get_executed_persons(self, name: str) -> dict:
        """
        获取被执行人信息
        
        Args:
            name: 公司全称
            
        Returns:
            被执行人列表
        """
        url = f"{self.base_url_v3}/executedPersons.json"
        params = {'name': urllib.parse.quote(name)}
        
        data = self._make_request(url, params)
        
        if data.get('error_code') == 0:
            items = data.get('result', [])
            print(f"✅ 成功获取被执行人信息，共 {len(items)} 条")
            return items
        else:
            print(f"❌ 获取被执行人信息失败: {data.get('reason')}")
            return []
    
    def get_abnormal_info(self, name: str) -> dict:
        """
        获取经营异常信息
        
        Args:
            name: 公司全称
            
        Returns:
            经营异常列表
        """
        url = f"{self.base_url_v3}/abnormal.json"
        params = {'name': urllib.parse.quote(name)}
        
        data = self._make_request(url, params)
        
        if data.get('error_code') == 0:
            items = data.get('result', [])
            print(f"✅ 成功获取经营异常信息，共 {len(items)} 条")
            return items
        else:
            print(f"❌ 获取经营异常信息失败: {data.get('reason')}")
            return []
    
    def get_administrative_penalty(self, name: str) -> dict:
        """
        获取行政处罚信息
        
        Args:
            name: 公司全称
            
        Returns:
            行政处罚列表
        """
        url = f"{self.base_url_v3}/punishment.json"
        params = {'name': urllib.parse.quote(name)}
        
        data = self._make_request(url, params)
        
        if data.get('error_code') == 0:
            items = data.get('result', {}).get('items', [])
            print(f"✅ 成功获取行政处罚信息，共 {len(items)} 条")
            return items
        else:
            print(f"❌ 获取行政处罚信息失败: {data.get('reason')}")
            return []
    
    def get_investment(self, name: str) -> dict:
        """
        获取对外投资信息
        
        Args:
            name: 公司全称
            
        Returns:
            对外投资列表
        """
        url = f"{self.base_url_v3}/findHistoryRongzi.json"
        params = {'name': urllib.parse.quote(name)}
        
        data = self._make_request(url, params)
        
        if data.get('error_code') == 0:
            items = data.get('result', {}).get('items', [])
            print(f"✅ 成功获取对外投资信息，共 {len(items)} 条")
            return items
        else:
            print(f"❌ 获取对外投资信息失败: {data.get('reason')}")
            return []
    
    def full_due_diligence(self, company_name: str) -> dict:
        """
        完整尽职调查
        
        Args:
            company_name: 公司全称
            
        Returns:
            完整的尽调报告数据
        """
        print(f"\n🔍 开始对 '{company_name}' 进行尽职调查...\n")
        
        result = {
            "company_name": company_name,
            "collection_time": datetime.now().isoformat(),
            "data": {}
        }
        
        # 1. 企业搜索获取ID
        search_result = self.search_company(company_name)
        result["data"]["search"] = search_result
        
        company_id = None
        if search_result.get("error_code") == 0:
            items = search_result.get("result", {}).get("items", [])
            if items:
                company_id = items[0].get("id")
        
        # 2. 基础信息
        result["data"]["base_info"] = self.get_base_info_v4(company_name)
        
        # 3. 股东信息
        result["data"]["shareholders"] = self.get_shareholders(company_name)
        
        # 4. 股权结构
        if company_id:
            result["data"]["equity_structure"] = self.get_equity_structure(company_id)
        
        # 5. 风险信息
        result["data"]["lawsuits"] = self.get_lawsuits(company_name)
        result["data"]["executed_persons"] = self.get_executed_persons(company_name)
        result["data"]["abnormal_info"] = self.get_abnormal_info(company_name)
        result["data"]["administrative_penalty"] = self.get_administrative_penalty(company_name)
        
        # 6. 对外投资
        result["data"]["investment"] = self.get_investment(company_name)
        
        print(f"\n✅ 尽职调查完成！\n")
        return result


# ================= 使用示例 =================
if __name__ == "__main__":
    import os
    
    # 从环境变量读取Token（推荐）
    TYC_TOKEN = os.getenv("TIANYANCHA_TOKEN", "your_token_here")
    
    if TYC_TOKEN == "your_token_here":
        print("⚠️  请先设置天眼查API Token:")
        print("   export TIANYANCHA_TOKEN='your_token'")
        exit(1)
    
    # 初始化API
    tyc = TianyanchaAPI(TYC_TOKEN)
    
    # 测试公司
    company_name = "广东横琴深水云科数字科技有限公司"
    
    print("=" * 60)
    print("天眼查 API 测试")
    print("=" * 60)
    
    # 1. 获取基本信息
    print("\n📋 1. 企业基本信息:")
    info = tyc.get_base_info_v4(company_name)
    if info:
        print(f"   公司名称: {info.get('name')}")
        print(f"   法人代表: {info.get('legalPersonName')}")
        print(f"   注册资本: {info.get('regCapital')}")
        print(f"   成立日期: {info.get('estiblishTime')}")
        print(f"   经营状态: {info.get('regStatus')}")
        print(f"   统一信用代码: {info.get('creditCode')}")
    
    # 2. 获取股东信息
    print("\n📊 2. 核心股东列表:")
    shareholders = tyc.get_shareholders(company_name)
    if shareholders:
        for i, sh in enumerate(shareholders[:5], 1):
            name = sh.get('name', '未知')
            ratio = sh.get('cgbl', sh.get('percent', '未知'))
            print(f"   {i}. {name}: 持股比例 {ratio}")
    
    # 3. 风险扫描
    print("\n⚠️  3. 风险信息扫描:")
    
    lawsuits = tyc.get_lawsuits(company_name)
    if lawsuits and lawsuits.get('total', 0) > 0:
        print(f"   法律诉讼: {lawsuits['total']} 条")
    else:
        print("   法律诉讼: 无")
    
    executed = tyc.get_executed_persons(company_name)
    if executed:
        print(f"   被执行人: {len(executed)} 条")
    else:
        print("   被执行人: 无")
    
    abnormal = tyc.get_abnormal_info(company_name)
    if abnormal:
        print(f"   经营异常: {len(abnormal)} 条")
    else:
        print("   经营异常: 无")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
