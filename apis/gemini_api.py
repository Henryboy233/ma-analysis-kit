#!/usr/bin/env python3
"""
Gemini AI 分析模块
用于商业尽调的AI增强分析
"""

import requests
import json
import os
from typing import Optional

# 配置API密钥和基础URL
import os
API_KEY = os.getenv("GEMINI_API_KEY", "")
BASE_URL = "https://api.tokenops.ai/v1beta"


class GeminiAnalyzer:
    """
    Gemini AI 分析器
    用于商业尽调的智能分析
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化
        
        Args:
            api_key: API密钥（可选，使用默认配置）
        """
        self.api_key = api_key or API_KEY
        self.base_url = BASE_URL
        self.model = "gemini-3.1-pro-preview"
    
    def analyze_due_diligence(self, company_name: str, industry: str, 
                             file_contents: list, financial_data: dict) -> str:
        """
        AI增强商业尽调分析
        
        Args:
            company_name: 公司名称
            industry: 行业
            file_contents: 上传文件内容列表
            financial_data: 财务数据
            
        Returns:
            AI分析结果文本
        """
        # 构建提示词
        prompt = self._build_dd_prompt(company_name, industry, file_contents, financial_data)
        
        # 调用Gemini API
        return self._call_api(prompt)
    
    def _build_dd_prompt(self, company_name: str, industry: str,
                        file_contents: list, financial_data: dict) -> str:
        """构建尽调分析提示词（优化版，更简洁）"""
        
        # 整理文件内容摘要 - 限制更短，加快处理
        file_summaries = []
        if file_contents:
            for i, fc in enumerate(file_contents[:3]):  # 最多取3个文件
                content = fc.get('content', '')[:1000]  # 每个文件限制1000字符
                file_summaries.append(f"[{i+1}]{fc['name']}:{content[:500]}...")
        
        files_text = "\n".join(file_summaries) if file_summaries else "未上传"
        
        # 简化财务数据描述
        fin_summary = "非上市/无数据"
        if financial_data.get('is_listed'):
            fin_summary = "上市公司，有财务数据"
        
        prompt = f"""作为投资分析师，对【{company_name}】({industry})进行快速尽调分析。

资料：{files_text}
财务：{fin_summary}

请输出简洁分析（控制在800字内）：

## 1. 商业模式
核心价值主张、盈利模式可持续性

## 2. 竞争优势  
核心优势、护城河评估（强/中/弱）

## 3. 财务健康度
关键指标趋势、主要风险点

## 4. 行业前景
行业趋势、竞争格局、公司地位

## 5. 投资风险
3个主要风险（高/中/低）

## 6. 投资建议
结论：建议/谨慎/观望 | 关键关注点

要求：观点明确、数据支撑、语言简练。"""
        
        return prompt
    
    def analyze_business_model(self, content: str) -> str:
        """
        分析商业模式
        
        Args:
            content: 商业计划书或相关资料内容
            
        Returns:
            商业模式分析
        """
        prompt = f"""请分析以下商业计划书内容，提取并总结其商业模式：

{content[:3000]}

请按以下框架分析：
1. 价值主张：解决什么痛点？
2. 目标客户：服务谁？
3. 产品/服务：提供什么？
4. 盈利模式：如何赚钱？
5. 关键资源：需要什么核心资源？
6. 渠道通路：如何触达客户？
7. 成本结构：主要成本是什么？
"""
        return self._call_api(prompt)
    
    def analyze_risks(self, company_info: str) -> str:
        """
        风险分析
        
        Args:
            company_info: 公司信息文本
            
        Returns:
            风险分析结果
        """
        prompt = f"""作为投资风控专家，请分析以下公司的潜在风险：

{company_info}

请从以下维度分析：
1. 市场风险
2. 经营风险
3. 财务风险
4. 合规风险
5. 团队风险

对每个风险给出：风险等级（高/中/低）、风险描述、影响程度。"""
        return self._call_api(prompt)
    
    def _call_api(self, message: str, timeout: int = 60) -> str:
        """
        调用Gemini API（非流式，快速返回）
        
        Args:
            message: 输入消息
            timeout: 超时时间（秒）
            
        Returns:
            API返回的文本
        """
        # 使用非流式接口，响应更快
        url = f"{self.base_url}/models/{self.model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": message
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 8192,
                "topP": 0.8,
                "topK": 40
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, 
                                   timeout=timeout)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                result = response.json()
                # 解析非流式响应
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        parts = candidate['content']['parts']
                        return ''.join([p.get('text', '') for p in parts])
                return "API返回格式异常"
            else:
                error_msg = f"API调用失败: HTTP {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail.get('error', {}).get('message', response.text[:200])}"
                except:
                    error_msg += f" - {response.text[:200]}"
                return error_msg
                
        except requests.exceptions.Timeout:
            return "API调用超时（60秒），请稍后重试。可能原因：当前请求量较大或网络延迟。"
        except requests.exceptions.ConnectionError:
            return "网络连接失败，请检查网络后重试。"
        except Exception as e:
            return f"API调用异常: {str(e)}"
    
    def analyze_due_diligence_stream(self, company_name: str, industry: str, 
                                     file_contents: list, financial_data: dict,
                                     placeholder=None):
        """
        流式AI尽调分析 - 实时显示结果
        
        Args:
            company_name: 公司名称
            industry: 行业
            file_contents: 上传文件内容列表
            financial_data: 财务数据
            placeholder: Streamlit占位符对象，用于实时更新显示
            
        Yields:
            每次生成的文本片段
        """
        # 构建提示词
        prompt = self._build_dd_prompt(company_name, industry, file_contents, financial_data)
        
        # 流式调用API
        url = f"{self.base_url}/models/{self.model}:streamGenerateContent"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 8192
            }
        }
        
        full_response = ""
        
        try:
            response = requests.post(url, headers=headers, json=data, 
                                   stream=True, timeout=60)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                for line in response.iter_lines(decode_unicode=True):
                    if line.strip():
                        # 去掉 SSE 的 "data: " 前缀
                        if line.startswith("data: "):
                            line = line[6:]
                        try:
                            chunk = json.loads(line)
                            if 'candidates' in chunk and len(chunk['candidates']) > 0:
                                candidate = chunk['candidates'][0]
                                if 'content' in candidate and 'parts' in candidate['content']:
                                    for part in candidate['content']['parts']:
                                        if 'text' in part:
                                            text_chunk = part['text']
                                            full_response += text_chunk
                                            # 实时更新显示
                                            if placeholder:
                                                placeholder.markdown(full_response + "▌")
                                            yield text_chunk
                        except json.JSONDecodeError:
                            continue
                
                # 最终更新（去掉光标）
                if placeholder:
                    placeholder.markdown(full_response)
                    
            else:
                error_msg = f"API调用失败: HTTP {response.status_code}"
                if placeholder:
                    placeholder.error(error_msg)
                    
        except Exception as e:
            error_msg = f"流式调用异常: {str(e)}"
            if placeholder:
                placeholder.error(error_msg)
        
        return full_response


# 测试代码
if __name__ == "__main__":
    analyzer = GeminiAnalyzer()
    result = analyzer.analyze_due_diligence(
        company_name="测试公司",
        industry="科技",
        file_contents=[],
        financial_data={}
    )
    print(result)
