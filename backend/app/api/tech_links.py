"""
技术链接增强API端点
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from ..services.tech_link_generator import tech_link_generator


router = APIRouter(prefix="/api/tech-links", tags=["技术链接"])


class MarkdownEnhanceRequest(BaseModel):
    """Markdown增强请求"""
    markdown: str


class MarkdownEnhanceResponse(BaseModel):
    """Markdown增强响应"""
    success: bool
    enhanced_markdown: str
    error: str = ""


@router.post("/enhance", response_model=MarkdownEnhanceResponse)
async def enhance_markdown(request: MarkdownEnhanceRequest):
    """
    增强markdown文本，添加技术文档链接
    
    Args:
        request: 包含原始markdown的请求
        
    Returns:
        MarkdownEnhanceResponse: 增强后的markdown（失败时返回原文）
    """
    try:
        # 验证输入
        if not request.markdown:
            return MarkdownEnhanceResponse(
                success=False,
                enhanced_markdown="",
                error="markdown内容不能为空"
            )
        
        # 调用服务生成增强的markdown
        enhanced_markdown = await tech_link_generator.enhance_markdown_with_links(
            request.markdown
        )
        
        return MarkdownEnhanceResponse(
            success=True,
            enhanced_markdown=enhanced_markdown
        )
        
    except Exception as e:
        # 发生任何错误，返回原始markdown
        print(f"API处理失败: {e}")
        return MarkdownEnhanceResponse(
            success=False,
            enhanced_markdown=request.markdown,
            error=str(e)
        )

