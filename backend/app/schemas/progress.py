from pydantic import BaseModel
from typing import Optional


class ProgressUpdate(BaseModel):
    """更新学习进度"""
    learning_path_id: int
    content_id: str
    content_type: str
    mastered: Optional[bool] = None
    needs_review: Optional[bool] = None


class ProgressResponse(BaseModel):
    """进度响应"""
    id: int
    user_id: int
    learning_path_id: int
    content_id: str
    content_type: str
    mastered: bool
    needs_review: bool
    
    class Config:
        from_attributes = True


class ProgressStats(BaseModel):
    """学习统计"""
    total_items: int
    mastered_items: int
    review_items: int
    mastery_rate: float

