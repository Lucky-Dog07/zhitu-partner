"""
AI助手API端点
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
from ..core.database import get_db
from .deps import get_current_user
from ..models.user import User
from ..services.ai_assistant_service import ai_assistant_service


router = APIRouter()


# Request/Response Models
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    success: bool
    message: str
    error: str = None


class HistoryMessage(BaseModel):
    id: int
    role: str
    message: str
    created_at: str


class QuickAction(BaseModel):
    id: str
    title: str
    description: str
    prompt: str
    icon: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    发送消息给AI助手
    
    Args:
        request: 包含用户消息的请求
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        AI的回复
    """
    try:
        result = ai_assistant_service.chat(
            user_id=current_user.id,
            message=request.message,
            db=db
        )
        return ChatResponse(**result)
    except Exception as e:
        import traceback
        print(f"[ERROR] AI助手聊天完整错误:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"聊天失败: {str(e)}")


@router.get("/history", response_model=List[HistoryMessage])
async def get_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """
    获取对话历史
    
    Args:
        limit: 返回的消息数量
        current_user: 当前登录用户
        
    Returns:
        对话历史列表
    """
    try:
        history = ai_assistant_service.get_conversation_history(
            user_id=current_user.id,
            limit=limit
        )
        return [HistoryMessage(**msg) for msg in history]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")


@router.delete("/history")
async def clear_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    清空对话历史
    
    Args:
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        操作结果
    """
    try:
        success = ai_assistant_service.clear_history(
            user_id=current_user.id,
            db=db
        )
        if success:
            return {"success": True, "message": "对话历史已清空"}
        else:
            raise HTTPException(status_code=500, detail="清空失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空历史失败: {str(e)}")


@router.get("/quick-actions", response_model=List[QuickAction])
async def get_quick_actions():
    """
    获取快捷功能列表
    
    Returns:
        快捷功能配置
    """
    try:
        actions = ai_assistant_service.get_quick_actions()
        return [QuickAction(**action) for action in actions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取快捷功能失败: {str(e)}")

