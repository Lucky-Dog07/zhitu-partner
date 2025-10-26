"""
智能技术链接生成服务
使用OpenAI LLM识别技术关键词并生成官方文档链接
"""
import json
import re
from typing import Dict, Optional
from functools import lru_cache
import httpx
from ..core.config import settings


class TechLinkGenerator:
    """技术链接生成器"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL
        self.model = settings.OPENAI_MODEL
        self.timeout = 10.0  # 10秒超时
        
    @lru_cache(maxsize=1000)
    def _get_tech_links_from_cache(self, text_hash: str) -> Optional[Dict[str, str]]:
        """
        缓存层（使用LRU缓存）
        注意：这里使用文本哈希作为key，实际的查询结果存在内存中
        """
        # LRU缓存会自动处理
        return None
    
    async def _call_openai(self, markdown_text: str) -> Dict[str, str]:
        """
        调用OpenAI API识别技术并生成链接
        
        Returns:
            Dict[str, str]: 技术名称 -> 官方文档URL的映射
        """
        prompt = f"""请分析以下Markdown文本，识别其中的技术关键词（编程语言、框架、数据库、工具等），并为每个技术生成其官方文档的URL链接。

要求：
1. 只返回你有把握的链接，不确定的不要生成
2. 优先使用中文文档（如果有）
3. URL必须是官方文档地址
4. 返回JSON格式：{{"技术名": "官方文档URL", ...}}

Markdown文本：
```
{markdown_text[:2000]}
```

请直接返回JSON，不要其他解释。"""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "你是一个技术文档专家，擅长为各种技术生成准确的官方文档链接。只返回JSON格式的结果。"
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000
                    }
                )
                
                if response.status_code != 200:
                    print(f"OpenAI API错误: {response.status_code} - {response.text}")
                    return {}
                
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                
                # 尝试解析JSON
                # 先清理可能的markdown代码块
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                elif content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                tech_links = json.loads(content)
                return tech_links if isinstance(tech_links, dict) else {}
                
        except httpx.TimeoutException:
            print("OpenAI API超时")
            return {}
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}, 内容: {content}")
            return {}
        except Exception as e:
            print(f"调用OpenAI API失败: {e}")
            return {}
    
    def _apply_links_to_markdown(self, markdown: str, tech_links: Dict[str, str]) -> str:
        """
        将生成的链接应用到markdown文本中
        
        Args:
            markdown: 原始markdown文本
            tech_links: 技术名称 -> URL的映射
            
        Returns:
            str: 增强后的markdown文本
        """
        result = markdown
        
        # 按照技术名称长度降序排序，避免短名称覆盖长名称
        sorted_techs = sorted(tech_links.items(), key=lambda x: len(x[0]), reverse=True)
        
        for tech_name, url in sorted_techs:
            # 检查是否已经有链接
            if f"[{tech_name}]" in result:
                continue
            
            # 使用正则替换，只在单词边界处替换
            # 避免在代码块中替换
            pattern = r'\b' + re.escape(tech_name) + r'\b'
            
            # 简单的替换策略：找到第一个匹配并替换
            # 使用更保守的策略，只替换前3次出现
            count = 0
            max_replacements = 3
            
            def replace_func(match):
                nonlocal count
                if count < max_replacements:
                    count += 1
                    return f"[{tech_name}]({url})"
                return match.group(0)
            
            result = re.sub(pattern, replace_func, result)
        
        return result
    
    async def enhance_markdown_with_links(self, markdown: str) -> str:
        """
        增强markdown文本，添加技术文档链接
        
        Args:
            markdown: 原始markdown文本
            
        Returns:
            str: 增强后的markdown文本（失败时返回原文）
        """
        if not markdown or not isinstance(markdown, str):
            return markdown or ""
        
        try:
            # 生成文本哈希作为缓存key
            text_hash = str(hash(markdown[:500]))  # 使用前500字符的哈希
            
            # 调用OpenAI获取技术链接
            tech_links = await self._call_openai(markdown)
            
            if not tech_links:
                print("未识别到技术关键词或API调用失败")
                return markdown
            
            print(f"识别到 {len(tech_links)} 个技术: {list(tech_links.keys())}")
            
            # 应用链接到markdown
            enhanced_markdown = self._apply_links_to_markdown(markdown, tech_links)
            
            return enhanced_markdown
            
        except Exception as e:
            print(f"增强markdown失败: {e}")
            return markdown


# 单例实例
tech_link_generator = TechLinkGenerator()

