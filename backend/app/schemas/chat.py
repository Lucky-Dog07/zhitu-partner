from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class ChatMessage(BaseModel):
    """聊天消息"""
    message: str
    context: Optional[str] = None  # 可选的上下文信息


class ChatResponse(BaseModel):
    """聊天响应"""
    role: str
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatHistoryList(BaseModel):
    """对话历史列表"""
    messages: List[ChatResponse]

