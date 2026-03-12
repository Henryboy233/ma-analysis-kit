#!/usr/bin/env python3
"""
收并购分析 - 报告生成脚本
MA Analysis - Report Generator

功能:
1. 读取数据文件
2. 生成分析报告 (Markdown)
3. 生成可视化图表
4. 导出Excel模型

使用方法:
    python report_generator.py --input ./data/ --template ../templates/report-template.md --output ./report/
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 非交互式后端


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, template_path: str, output_dir: str = "./report"):
        self.template_path = Path(template_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载模板
        with open(self.template_path, 'r', encoding='utf-8') as f:
            self.template = f.read()
    
    def fill_template(self, data: Dict) -> str:
        """填充模板变量"""
        result = self.template
        
        # 简单变量替换 {{variable}}
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        return result
    
    def generate_charts(self, financial_data: Dict, company_name: str) -> List[str]:
        """生成财务图表"""
        chart_files = []
        
        # 收入趋势图
        if 'revenue_history' in financial_data:
            years = list(financial_data['revenue_history'].keys())
            revenues = list(financial_data['revenue_history'].values())
            
            plt.figure(figsize=(10, 6))
            plt.plot(years, revenues, marker='o', linewidth=2)
            plt.title(f'{company_name} - 收入趋势')
            plt.xlabel('年度')
            plt.ylabel('收入 (万元)')
            plt.grid(True, alpha=0.3)
            
            chart_path = self.output_dir / f'{company_name}_revenue_trend.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            chart_files.append(str(chart_path))
            print(f"Chart saved: {chart_path}")
        
        # 利润率趋势图
        if 'margin_history' in financial_data:
            years = list(financial_data['margin_history'].keys())
            margins = list(financial_data['margin_history'].values())
            
            plt.figure(figsize=(10, 6))
            plt.plot(years, margins, marker='s', color='green', linewidth=2)
            plt.title(f'{company_name} - 利润率趋势')
            plt.xlabel('年度')
            plt.ylabel('净利率 (%)')
            plt.grid(True, alpha=0.3)
            
            chart_path = self.output_dir / f'{company_name}_margin_trend.png'
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            chart_files.append(str(chart_path))
            print(f"Chart saved: {chart_path}")
        
        return chart_files
    
    def generate_excel_model(self, data: Dict, company_name: str) -> str:
        """生成Excel财务模型"""
        excel_path = self.output_dir / f'{company_name}_财务模型.xlsx'
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # 假设数据
            years = ['2022', '2023', '2024', '2025E', '2026E', '2027E']
            
            # 利润表
            income_stmt = pd.DataFrame({
                '科目': ['营业收入', '营业成本', '毛利', '销售费用', '管理费用', 
                        '研发费用', '营业利润', '净利润'],
                '2022': [1000, 600, 400, 50, 80, 70, 200, 150],
                '2023': [1200, 720, 480, 60, 90, 80, 250, 188],
                '2024': [1500, 900, 600, 75, 100, 100, 325, 244],
                '2025E': [1800, 1080, 720, 90, 110, 120, 400, 300],
                '2026E': [2100, 1260, 840, 105, 120, 140, 475, 356],
                '2027E': [2400, 1440, 960, 120, 130, 160, 550, 413]
            })
            income_stmt.to_excel(writer, sheet_name='利润表', index=False)
            
            # DCF模型
            dcf = pd.DataFrame({
                '年份': ['1', '2', '3', '4', '5', '终值'],
                '自由现金流': [200, 240, 290, 350, 420, 5000],
                '折现因子': [0.909, 0.826, 0.751, 0.683, 0.621, 0.621],
                '现值': [182, 198, 218, 239, 261, 3105]
            })
            dcf.to_excel(writer, sheet_name='DCF模型', index=False)
            
            # 敏感性分析
            sensitivity = pd.DataFrame({
                'WACC \\ 永续增长率': ['1.0%', '2.0%', '3.0%'],
                '8.0%': [3500, 3800, 4200],
                '9.0%': [3200, 3500, 3800],
                '10.0%': [2900, 3200, 3500],
                '11.0%': [2600, 2900, 3200]
            })
            sensitivity.to_excel(writer, sheet_name='敏感性分析', index=False)
        
        print(f"Excel model saved: {excel_path}")
        return str(excel_path)
    
    def generate_report(self, data: Dict, company_name: str) -> str:
        """生成完整报告"""
        # 填充模板
        report_content = self.fill_template(data)
        
        # 保存Markdown报告
        report_path = self.output_dir / f'{company_name}_分析报告.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"Report saved: {report_path}")
        return str(report_path)


class DataLoader:
    """数据加载器"""
    
    @staticmethod
    def load_json(filepath: str) -> Dict:
        """加载JSON数据"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def load_all_data(input_dir: str) -> Dict:
        """加载目录下所有数据文件"""
        input_path = Path(input_dir)
        all_data = {}
        
        for json_file in input_path.glob('**/*.json'):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data[json_file.stem] = data
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
        
        return all_data
    
    @staticmethod
    def extract_company_info(data: Dict) -> Dict:
        """提取公司信息"""
        # 从各种数据源提取公司信息
        company_info = {
            "company_name": "目标公司",
            "company_full_name": "目标公司全称",
            "credit_code": "",
            "establish_date": "",
            "registered_capital": 0,
            "legal_representative": "",
            "industry": ""
        }
        
        # 从天眼查数据提取
        if 'tianyancha' in data:
            tyc_data = data['tianyancha']
            # 解析天眼查数据...
        
        return company_info


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='收并购报告生成工具')
    
    parser.add_argument('--input', '-i', type=str, required=True, 
                       help='输入数据目录')
    parser.add_argument('--template', '-t', type=str, 
                       default='../templates/report-template.md',
                       help='报告模板路径')
    parser.add_argument('--output', '-o', type=str, default='./report',
                       help='输出目录')
    parser.add_argument('--company', '-c', type=str, required=True,
                       help='公司名称')
    parser.add_argument('--format', '-f', type=str, default='all',
                       choices=['md', 'excel', 'charts', 'all'],
                       help='输出格式')
    
    args = parser.parse_args()
    
    # 加载数据
    print(f"Loading data from: {args.input}")
    data = DataLoader.load_all_data(args.input)
    
    # 提取公司信息
    company_info = DataLoader.extract_company_info(data)
    company_info['company_name'] = args.company
    company_info['report_date'] = datetime.now().strftime('%Y-%m-%d')
    company_info['report_id'] = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # 初始化报告生成器
    generator = ReportGenerator(args.template, args.output)
    
    # 生成报告
    if args.format in ['md', 'all']:
        print("\nGenerating Markdown report...")
        generator.generate_report(company_info, args.company)
    
    # 生成Excel模型
    if args.format in ['excel', 'all']:
        print("\nGenerating Excel model...")
        generator.generate_excel_model(data, args.company)
    
    # 生成图表
    if args.format in ['charts', 'all']:
        print("\nGenerating charts...")
        financial_data = {
            'revenue_history': {'2022': 1000, '2023': 1200, '2024': 1500},
            'margin_history': {'2022': 15, '2023': 15.6, '2024': 16.3}
        }
        generator.generate_charts(financial_data, args.company)
    
    print(f"\n✓ 报告生成完成! 输出目录: {args.output}")


if __name__ == '__main__':
    main()
