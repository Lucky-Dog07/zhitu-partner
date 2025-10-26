from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from ..core.database import get_db
from ..api.deps import get_current_user
from ..models.user import User
from ..models.interview_session import InterviewSession
from ..services.interview_simulator import InterviewSimulator
from pydantic import BaseModel


router = APIRouter()


class StartSessionRequest(BaseModel):
    learning_path_id: int


class ContinueConversationRequest(BaseModel):
    session_id: int
    answer: str


class EndSessionRequest(BaseModel):
    session_id: int


@router.post("/start")
async def start_interview_session(
    request: StartSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """开始新的面试模拟会话"""
    try:
        simulator = InterviewSimulator(db)
        result = simulator.start_session(current_user.id, request.learning_path_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动面试失败：{str(e)}")


@router.post("/continue")
async def continue_interview(
    request: ContinueConversationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """继续面试对话"""
    try:
        simulator = InterviewSimulator(db)
        result = simulator.continue_conversation(
            request.session_id,
            current_user.id,
            request.answer
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败：{str(e)}")


@router.post("/end")
async def end_interview_session(
    request: EndSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """结束面试，生成评价报告"""
    try:
        simulator = InterviewSimulator(db)
        result = simulator.end_session(request.session_id, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"结束面试失败：{str(e)}")


@router.get("/history")
async def get_interview_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取历史面试记录"""
    try:
        sessions = db.query(InterviewSession).filter(
            InterviewSession.user_id == current_user.id,
            InterviewSession.status == "completed"
        ).order_by(InterviewSession.created_at.desc()).limit(limit).all()
        
        return [{
            "id": s.id,
            "position": s.position,
            "score": s.evaluation.get("overall_score") if s.evaluation else None,
            "duration_minutes": s.duration_seconds // 60 if s.duration_seconds else 0,
            "started_at": s.started_at.isoformat()
        } for s in sessions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败：{str(e)}")


@router.get("/session/{session_id}")
async def get_session_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取面试会话详情（用于复习）"""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return {
        "id": session.id,
        "position": session.position,
        "status": session.status,
        "conversation": session.conversation,
        "evaluation": session.evaluation,
        "duration_minutes": session.duration_seconds // 60 if session.duration_seconds else 0
    }

