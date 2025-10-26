from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class NoteCreate(BaseModel):
    """创建笔记"""
    notebook_id: int
    title: Optional[str] = None
    content: str
    tags: List[str] = []
    editor_mode: str = 'markdown'
    learning_path_id: Optional[int] = None


class NoteUpdate(BaseModel):
    """更新笔记"""
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class NoteResponse(BaseModel):
    """笔记响应"""
    id: int
    user_id: int
    notebook_id: Optional[int] = None
    title: Optional[str] = None
    content: str
    tags: List[str]
    editor_mode: str = 'markdown'
    learning_path_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

