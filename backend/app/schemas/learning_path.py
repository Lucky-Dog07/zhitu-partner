from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, List


class LearningPathCreate(BaseModel):
    """创建学习路线请求"""
    position: str
    job_description: str
    content_types: Optional[List[str]] = ['mindmap']  # 默认只生成思维导图


class ContentGenerationRequest(BaseModel):
    """按需生成内容请求"""
    content_type: str  # knowledge, interview, courses, books, certifications


class LearningPathResponse(BaseModel):
    """学习路线响应"""
    id: int
    user_id: int
    position: str
    job_description: Optional[str] = None
    generated_content: Optional[Any] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class LearningPathList(BaseModel):
    """学习路线列表"""
    total: int
    items: List[LearningPathResponse]

