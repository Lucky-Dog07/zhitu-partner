from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotebookBase(BaseModel):
    """笔记本基础模型"""
    name: str
    description: Optional[str] = None
    icon: str = "📚"


class NotebookCreate(NotebookBase):
    """创建笔记本"""
    pass


class NotebookUpdate(BaseModel):
    """更新笔记本"""
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None


class NotebookResponse(NotebookBase):
    """笔记本响应"""
    id: int
    user_id: int
    is_default: bool
    note_count: Optional[int] = 0
    created_at: datetime
    
    class Config:
        from_attributes = True

