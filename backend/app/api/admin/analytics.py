from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ...core.database import get_db
from ...api.deps import get_current_admin
from ...models.user import User
from ...models.learning_path import LearningPath
from ...models.note import Note
from ...models.interview_question import InterviewQuestion

router = APIRouter()


@router.get("/overview")
async def get_overview(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取数据概览"""
    # 总用户数
    total_users = db.query(func.count(User.id)).scalar()
    
    # 今日活跃用户（最近24小时登录）
    today_active = db.query(func.count(User.id)).filter(
        User.last_login_at >= datetime.utcnow() - timedelta(days=1)
    ).scalar()
    
    # 本周新增用户
    week_new_users = db.query(func.count(User.id)).filter(
        User.created_at >= datetime.utcnow() - timedelta(days=7)
    ).scalar()
    
    # 学习路线总数
    total_learning_paths = db.query(func.count(LearningPath.id)).scalar()
    
    # 笔记总数
    total_notes = db.query(func.count(Note.id)).scalar()
    
    # 面试题总数
    total_questions = db.query(func.count(InterviewQuestion.id)).scalar()
    
    return {
        "total_users": total_users,
        "today_active_users": today_active,
        "week_new_users": week_new_users,
        "total_learning_paths": total_learning_paths,
        "total_notes": total_notes,
        "total_questions": total_questions
    }


@router.get("/users/growth")
async def get_user_growth(
    days: int = 30,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取用户增长趋势"""
    # 简化实现：返回每天的新增用户数
    growth_data = []
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days-i-1)
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        count = db.query(func.count(User.id)).filter(
            User.created_at >= start_date,
            User.created_at < end_date
        ).scalar()
        
        growth_data.append({
            "date": start_date.strftime("%Y-%m-%d"),
            "count": count
        })
    
    return growth_data


@router.get("/features/usage")
async def get_features_usage(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取功能使用统计"""
    learning_paths_count = db.query(func.count(LearningPath.id)).scalar()
    notes_count = db.query(func.count(Note.id)).scalar()
    questions_count = db.query(func.count(InterviewQuestion.id)).scalar()
    
    # AI助手使用次数（如果有chat_history表的话）
    # chat_count = db.query(func.count(ChatHistory.id)).scalar()
    
    return {
        "learning_paths": learning_paths_count,
        "notes": notes_count,
        "interview_questions": questions_count,
        # "ai_chat": chat_count
    }

