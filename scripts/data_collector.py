#!/usr/bin/env python3
"""
收并购分析 - 数据采集脚本
MA Analysis - Data Collection Script

功能:
1. 工商信息采集
2. 新闻舆情监控
3. 公告下载 (上市公司)
4. 数据标准化输出

使用方法:
    python data_collector.py --company "公司名称" --output ./data/
    python data_collector.py --stock-code 301038 --report-types annual --years 3
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import requests


class DataCollector:
    """数据采集器基类"""
    
    def __init__(self, output_dir: str = "./data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def save_json(self, data: Dict, filename: str):
        """保存JSON数据"""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved: {filepath}")
        return filepath
    
    def save_text(self, content: str, filename: str):
        """保存文本数据"""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved: {filepath}")
        return filepath


class TianyanchaCollector(DataCollector):
    """天眼查数据采集 (需要API Key)"""
    
    BASE_URL = "https://api.tianyancha.com/services/v3"
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or os.getenv('TIANYANCHA_API_KEY')
        if not self.api_key:
            print("Warning: Tianyancha API key not provided")
    
    def search_company(self, keyword: str) -> Dict:
        """搜索公司"""
        if not self.api_key:
            return {"error": "API key required"}
        
        url = f"{self.BASE_URL}/search/solrV2"
        params = {"key": self.api_key, "keyword": keyword}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_company_detail(self, company_id: str) -> Dict:
        """获取公司详情"""
        if not self.api_key:
            return {"error": "API key required"}
        
        url = f"{self.BASE_URL}/company/baseinfo"
        params = {"key": self.api_key, "id": company_id}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def collect(self, company_name: str) -> Dict:
        """完整采集"""
        print(f"\n[天眼查] 采集: {company_name}")
        
        # 搜索公司
        search_result = self.search_company(company_name)
        
        # 保存结果
        self.save_json(search_result, f"tianyancha_{company_name}.json")
        
        return search_result


class CninfoCollector(DataCollector):
    """巨潮资讯网数据采集 (上市公司公告)"""
    
    BASE_URL = "http://www.cninfo.com.cn/new/information"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = self.output_dir / "cninfo"
        self.output_dir.mkdir(exist_ok=True)
    
    def get_company_announcements(self, stock_code: str, 
                                   page_num: int = 1, 
                                   page_size: int = 30) -> Dict:
        """获取公司公告列表"""
        url = f"{self.BASE_URL}/announcement/query"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }
        
        data = {
            'pageNum': page_num,
            'pageSize': page_size,
            'tabName': 'fulltext',
            'column': 'szse' if stock_code.startswith(('00', '30')) else 'sse',
            'stock': stock_code,
            'searchkey': '',
            'secid': '',
            'plate': 'sz' if stock_code.startswith(('00', '30')) else 'sh',
            'category': 'category_ndbg_szsh,category_bndbg_szsh,category_yjdbg_szsh,category_sjdbg_szsh',
            'trade': '',
            'columnTitle': '历年公告',
            'sortName': '',
            'sortType': '',
            'limit': '',
            'showTitle': '',
            'seDate': ''
        }
        
        try:
            response = self.session.post(url, data=data, headers=headers, timeout=30)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def download_announcement(self, url: str, filename: str) -> str:
        """下载公告PDF"""
        try:
            response = self.session.get(url, timeout=60)
            filepath = self.output_dir / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"Download failed: {e}")
            return ""
    
    def collect(self, stock_code: str, years: int = 3) -> Dict:
        """完整采集"""
        print(f"\n[巨潮资讯] 采集: {stock_code}, 近{years}年")
        
        # 获取公告列表
        announcements = self.get_company_announcements(stock_code)
        
        # 保存列表
        self.save_json(announcements, f"{stock_code}_announcements.json")
        
        # 下载PDF (可选)
        if 'announcements' in announcements:
            for ann in announcements['announcements'][:5]:  # 只下载前5个
                if 'adjunctUrl' in ann:
                    pdf_url = f"http://static.cninfo.com.cn/{ann['adjunctUrl']}"
                    filename = f"{ann['announcementId']}.pdf"
                    self.download_announcement(pdf_url, filename)
                    time.sleep(1)  # 礼貌性延迟
        
        return announcements


class NewsCollector(DataCollector):
    """新闻舆情采集"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.output_dir = self.output_dir / "news"
        self.output_dir.mkdir(exist_ok=True)
    
    def search_news(self, keyword: str, days: int = 365) -> List[Dict]:
        """
        搜索新闻 (使用WebSearch API)
        注意: 这里使用模拟数据，实际使用时需要接入新闻API
        """
        print(f"Searching news for: {keyword} (past {days} days)")
        
        # TODO: 接入实际的新闻API
        # 如: 百度新闻API、搜狗API、或第三方服务
        
        mock_results = [
            {
                "title": f"{keyword} 发布最新财报",
                "source": "财经网",
                "date": "2026-01-15",
                "summary": f"{keyword} 2025年营收增长20%..."
            },
            {
                "title": f"{keyword} 宣布新一轮融资",
                "source": "36氪",
                "date": "2025-12-20",
                "summary": f"{keyword} 完成亿元级融资..."
            }
        ]
        
        return mock_results
    
    def collect(self, keywords: str, days: int = 365) -> Dict:
        """完整采集"""
        keyword_list = [k.strip() for k in keywords.split(',')]
        
        all_news = {}
        for keyword in keyword_list:
            print(f"\n[新闻] 采集: {keyword}")
            news = self.search_news(keyword, days)
            all_news[keyword] = news
            time.sleep(1)
        
        # 保存结果
        result = {
            "collection_date": datetime.now().isoformat(),
            "keywords": keyword_list,
            "days": days,
            "news": all_news
        }
        
        self.save_json(result, f"news_{datetime.now().strftime('%Y%m%d')}.json")
        
        return result


class AnalysisHelper:
    """分析辅助工具"""
    
    @staticmethod
    def calculate_financial_ratios(financial_data: Dict) -> Dict:
        """计算财务比率"""
        ratios = {}
        
        # 盈利能力
        if 'revenue' in financial_data and 'net_profit' in financial_data:
            revenue = financial_data['revenue']
            net_profit = financial_data['net_profit']
            if revenue > 0:
                ratios['net_margin'] = net_profit / revenue
        
        # 偿债能力
        if 'current_assets' in financial_data and 'current_liabilities' in financial_data:
            current_liabilities = financial_data['current_liabilities']
            if current_liabilities > 0:
                ratios['current_ratio'] = financial_data['current_assets'] / current_liabilities
        
        return ratios
    
    @staticmethod
    def generate_summary(data: Dict) -> str:
        """生成数据摘要"""
        summary = []
        summary.append(f"数据采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        summary.append(f"数据项数量: {len(data)}")
        
        return "\n".join(summary)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='收并购数据采集工具')
    
    parser.add_argument('--company', '-c', type=str, help='公司名称')
    parser.add_argument('--stock-code', '-s', type=str, help='股票代码')
    parser.add_argument('--keywords', '-k', type=str, help='新闻关键词 (逗号分隔)')
    parser.add_argument('--output', '-o', type=str, default='./data', help='输出目录')
    parser.add_argument('--sources', type=str, default='all', 
                       help='数据源: all, tianyancha, cninfo, news')
    parser.add_argument('--years', '-y', type=int, default=3, help='年报年份数')
    parser.add_argument('--days', '-d', type=int, default=365, help='新闻搜索天数')
    
    args = parser.parse_args()
    
    if not any([args.company, args.stock_code, args.keywords]):
        parser.print_help()
        sys.exit(1)
    
    results = {}
    
    # 天眼查采集
    if args.sources in ['all', 'tianyancha'] and args.company:
        tyc = TianyanchaCollector(output_dir=args.output)
        results['tianyancha'] = tyc.collect(args.company)
    
    # 巨潮资讯采集
    if args.sources in ['all', 'cninfo'] and args.stock_code:
        cninfo = CninfoCollector(output_dir=args.output)
        results['cninfo'] = cninfo.collect(args.stock_code, args.years)
    
    # 新闻采集
    if args.sources in ['all', 'news'] and args.keywords:
        news = NewsCollector(output_dir=args.output)
        results['news'] = news.collect(args.keywords, args.days)
    
    # 生成汇总报告
    if results:
        summary_file = Path(args.output) / f"collection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                "collection_time": datetime.now().isoformat(),
                "parameters": vars(args),
                "results_summary": {k: "success" if "error" not in str(v) else "failed" 
                                  for k, v in results.items()}
            }, f, ensure_ascii=False, indent=2)
        print(f"\nSummary saved: {summary_file}")
    
    print("\n采集完成!")


if __name__ == '__main__':
    main()
