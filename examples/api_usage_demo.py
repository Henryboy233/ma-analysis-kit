#!/usr/bin/env python3
"""
API 使用示例 - 收并购分析套件

本脚本演示如何使用天眼查和Tushare API进行公司分析
"""

import os
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from apis import TianyanchaAPI, TushareFinanceAPI
from apis.api_manager import APIManager


def demo_tianyancha():
    """
    天眼查 API 使用演示
    
    功能：获取非上市公司的工商信息和风险扫描
    """
    print("\n" + "=" * 70)
    print("演示1: 天眼查 API - 非上市公司尽调")
    print("=" * 70 + "\n")
    
    token = os.getenv("TIANYANCHA_TOKEN")
    if not token:
        print("⚠️  请设置环境变量: export TIANYANCHA_TOKEN='your_token'")
        return
    
    tyc = TianyanchaAPI(token)
    
    # 以深水云科为例
    company = "广东横琴深水云科数字科技有限公司"
    
    print(f"目标公司: {company}\n")
    
    # 1. 基础信息
    print("📋 工商基本信息:")
    info = tyc.get_base_info_v4(company)
    if info:
        print(f"  公司全称: {info.get('name')}")
        print(f"  法人代表: {info.get('legalPersonName')}")
        print(f"  注册资本: {info.get('regCapital')}")
        print(f"  成立日期: {info.get('estiblishTime')}")
        print(f"  经营状态: {info.get('regStatus')}")
        print(f"  统一信用代码: {info.get('creditCode')}")
        print(f"  注册地址: {info.get('regLocation')}")
    
    # 2. 股东信息
    print("\n📊 股东结构:")
    shareholders = tyc.get_shareholders(company)
    if shareholders:
        for i, sh in enumerate(shareholders[:5], 1):
            name = sh.get('name', '未知')
            ratio = sh.get('cgbl', sh.get('percent', '未知'))
            sh_type = '自然人' if sh.get('type') == 2 else '企业'
            print(f"  {i}. {name} ({sh_type}): {ratio}")
    
    # 3. 风险扫描
    print("\n⚠️  风险扫描:")
    
    lawsuits = tyc.get_lawsuits(company)
    lawsuit_count = lawsuits.get('total', 0) if lawsuits else 0
    print(f"  法律诉讼: {lawsuit_count} 条")
    
    executed = tyc.get_executed_persons(company)
    print(f"  被执行人: {len(executed)} 条")
    
    abnormal = tyc.get_abnormal_info(company)
    print(f"  经营异常: {len(abnormal)} 条")
    
    penalty = tyc.get_administrative_penalty(company)
    print(f"  行政处罚: {len(penalty)} 条")
    
    print("\n✅ 天眼查演示完成!")


def demo_tushare():
    """
    Tushare API 使用演示
    
    功能：获取A股上市公司的财务数据和估值指标
    """
    print("\n" + "=" * 70)
    print("演示2: Tushare API - A股上市公司分析")
    print("=" * 70 + "\n")
    
    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        print("⚠️  请设置环境变量: export TUSHARE_TOKEN='your_token'")
        print("   注册地址: https://tushare.pro/register")
        return
    
    ts = TushareFinanceAPI(token)
    
    # 以贵州茅台为例
    ts_code = "600519.SH"
    company_name = "贵州茅台"
    
    print(f"目标公司: {company_name} ({ts_code})\n")
    
    # 1. 公司基本信息
    print("📋 公司基本信息:")
    basic = ts.get_stock_basic(ts_code=ts_code)
    if not basic.empty:
        print(f"  股票代码: {basic.iloc[0]['ts_code']}")
        print(f"  公司名称: {basic.iloc[0]['name']}")
        print(f"  所属行业: {basic.iloc[0]['industry']}")
        print(f"  所属地区: {basic.iloc[0]['area']}")
        print(f"  上市日期: {basic.iloc[0]['list_date']}")
    
    # 2. 财务数据（近2年）
    print("\n📊 财务数据 (利润表):")
    income = ts.get_income_statement(ts_code, '20230101', '20241231')
    if not income.empty:
        # 显示最近4个季度
        recent = income.tail(4)
        for _, row in recent.iterrows():
            print(f"  报告期: {row['end_date']}")
            print(f"    营业收入: {row['total_revenue']:,.0f} 万元")
            print(f"    净利润: {row['n_income']:,.0f} 万元")
            if 'net_margin' in row:
                print(f"    净利率: {row['net_margin']:.2f}%")
            print()
    
    # 3. 估值指标
    print("💰 估值指标:")
    val = ts.get_valuation_metrics(ts_code)
    if not val.empty:
        v = val.iloc[0]
        print(f"  收盘价: {v['close']:.2f} 元")
        print(f"  市盈率(PE): {v['pe']:.2f}")
        print(f"  市盈率(TTM): {v['pe_ttm']:.2f}")
        print(f"  市净率(PB): {v['pb']:.2f}")
        print(f"  总市值: {v['total_mv']/10000:,.2f} 亿元")
    
    # 4. 可比公司
    print("\n🏭 同行业可比公司:")
    if not basic.empty:
        industry = basic.iloc[0]['industry']
        peers = ts.get_industry_peers(industry)
        if not peers.empty:
            print(f"  行业: {industry}")
            print(f"  同行业公司数: {len(peers)}")
            print("  前10家:")
            for _, row in peers.head(10).iterrows():
                print(f"    - {row['name']} ({row['ts_code']})")
    
    print("\n✅ Tushare演示完成!")


def demo_combined_analysis():
    """
    综合演示：使用APIManager进行完整分析
    """
    print("\n" + "=" * 70)
    print("演示3: 综合API管理器 - 一键完整分析")
    print("=" * 70 + "\n")
    
    # 检查配置
    if not os.getenv("TIANYANCHA_TOKEN") or not os.getenv("TUSHARE_TOKEN"):
        print("⚠️  请配置两个API的Token:")
        print("   export TIANYANCHA_TOKEN='your_tyc_token'")
        print("   export TUSHARE_TOKEN='your_ts_token'")
        return
    
    # 初始化管理器
    manager = APIManager()
    
    # 分析一家上市公司
    ts_code = "000001.SZ"  # 平安银行
    company_name = "平安银行股份有限公司"
    
    print(f"分析目标: {company_name} ({ts_code})\n")
    
    # 执行完整分析
    result = manager.full_analysis(ts_code, company_name)
    
    # 生成报告摘要
    summary = manager.generate_report_summary(result)
    
    print("\n生成的报告摘要:")
    print("-" * 70)
    print(summary)
    print("-" * 70)
    
    # 保存报告
    output_file = f"report_{ts_code.replace('.', '_')}.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(f"\n✅ 报告已保存到: {output_file}")


def main():
    """
    主函数：运行所有演示
    """
    print("\n" + "=" * 70)
    print("收并购分析套件 - API使用示例")
    print("=" * 70)
    
    # 检查环境
    has_tyc = bool(os.getenv("TIANYANCHA_TOKEN"))
    has_ts = bool(os.getenv("TUSHARE_TOKEN"))
    
    print("\n环境检查:")
    print(f"  天眼查Token: {'✅ 已配置' if has_tyc else '❌ 未配置'}")
    print(f"  TushareToken: {'✅ 已配置' if has_ts else '❌ 未配置'}")
    
    if not has_tyc and not has_ts:
        print("\n⚠️  请先配置至少一个API Token:")
        print("   1. 天眼查: https://open.tianyancha.com/")
        print("   2. Tushare: https://tushare.pro/register")
        print("\n   设置方法:")
        print("   export TIANYANCHA_TOKEN='your_token'")
        print("   export TUSHARE_TOKEN='your_token'")
        return
    
    # 运行演示
    if has_tyc:
        demo_tianyancha()
    
    if has_ts:
        demo_tushare()
    
    if has_tyc and has_ts:
        demo_combined_analysis()
    
    print("\n" + "=" * 70)
    print("所有演示完成!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
