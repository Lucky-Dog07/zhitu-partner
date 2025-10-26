from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..api.deps import get_current_user
from ..models.user import User
from ..models.chat_history import ChatHistory
from ..schemas.chat import ChatMessage, ChatResponse
from ..services.ai_assistant import ai_assistant

router = APIRouter(prefix="/api/chat", tags=["AI对话"])


@router.post("", response_model=ChatResponse)
async def chat_with_ai(
    chat_data: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """与AI助手对话"""
    # 获取最近的对话历史
    history_records = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.created_at.desc()).limit(10).all()
    
    # 构建历史对话列表
    chat_history = [
        {"role": record.role, "message": record.message}
        for record in reversed(history_records)
    ]
    
    # 调用AI助手
    try:
        ai_response = await ai_assistant.chat(
            message=chat_data.message,
            context=chat_data.context,
            chat_history=chat_history
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI助手响应失败: {str(e)}"
        )
    
    # 保存用户消息
    user_message = ChatHistory(
        user_id=current_user.id,
        role="user",
        message=chat_data.message
    )
    db.add(user_message)
    
    # 保存AI响应
    ai_message = ChatHistory(
        user_id=current_user.id,
        role="assistant",
        message=ai_response
    )
    db.add(ai_message)
    
    db.commit()
    db.refresh(ai_message)
    
    return ChatResponse.model_validate(ai_message)


@router.get("/history", response_model=List[ChatResponse])
async def get_chat_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取对话历史"""
    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.created_at.desc()).offset(skip).limit(limit).all()
    
    return [ChatResponse.model_validate(msg) for msg in reversed(history)]


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """清空对话历史"""
    db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).delete()
    db.commit()

