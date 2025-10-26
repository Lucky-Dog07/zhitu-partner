import httpx
from typing import Dict, Any, List
from ..core.config_manager import config


class N8NClient:
    """n8n工作流客户端"""
    
    def __init__(self):
        # 从配置文件加载n8n配置
        n8n_config = config.get_n8n_config()
        
        self.webhook_url = n8n_config.get('webhook_url', '')
        self.timeout = n8n_config.get('timeout', 120)
    
    async def generate_learning_path(
        self, 
        user_id: str, 
        position: str, 
        job_description: str,
        content_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        调用n8n工作流生成学习路线
        
        Args:
            user_id: 用户ID
            position: 职位名称
            job_description: 职位描述
            content_types: 需要生成的内容类型列表
            
        Returns:
            Dict containing success status and generated content
        """
        if content_types is None:
            content_types = ['mindmap']
        
        try:
            # 禁用代理，直接连接
            async with httpx.AsyncClient(
                timeout=self.timeout,
                proxies={}  # 显式设置为空字典以禁用代理
            ) as client:
                response = await client.post(
                    self.webhook_url,
                    json={
                        "user_id": user_id,
                        "position": position,
                        "job_description": job_description,
                        "content_types": content_types
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"[ERROR] n8n HTTP错误: {type(e).__name__}: {str(e)}")
            return {
                "success": False,
                "error": f"n8n工作流调用失败: {str(e)}"
            }
        except Exception as e:
            print(f"[ERROR] n8n未知错误: {type(e).__name__}: {str(e)}")
            return {
                "success": False,
                "error": f"未知错误: {str(e)}"
            }
    
    async def generate_specific_content(
        self,
        user_id: str,
        position: str,
        content_type: str,
        skills: List[str] = None
    ) -> Dict[str, Any]:
        """
        调用n8n工作流生成特定类型的内容
        
        Args:
            user_id: 用户ID
            position: 职位名称
            content_type: 内容类型 (knowledge, interview, courses, books, certifications)
            skills: 已提取的技能列表
            
        Returns:
            Dict containing success status and generated content
        """
        try:
            # 禁用代理，直接连接到localhost
            async with httpx.AsyncClient(
                timeout=60.0,
                proxies={}  # 显式设置为空字典以禁用代理
            ) as client:
                # 构建请求数据
                request_data = {
                    "user_id": user_id,
                    "position": position,
                    "content_type": content_type,
                    "content_types": [content_type]  # 兼容现有工作流
                }
                
                if skills:
                    request_data["skills"] = skills
                
                response = await client.post(
                    f"{self.base_url}{self.webhook_path}",
                    json=request_data
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"[ERROR] n8n内容生成HTTP错误: {type(e).__name__}: {str(e)}")
            return {
                "success": False,
                "error": f"内容生成失败: {str(e)}"
            }
        except Exception as e:
            print(f"[ERROR] n8n内容生成未知错误: {type(e).__name__}: {str(e)}")
            return {
                "success": False,
                "error": f"未知错误: {str(e)}"
            }


# 单例实例
n8n_client = N8NClient()

