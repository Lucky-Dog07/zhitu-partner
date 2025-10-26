from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from ..core.database import Base
import datetime


class InterviewSession(Base):
    """面试模拟会话"""
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"))
    
    # 面试信息
    position = Column(String(100))  # 面试职位
    status = Column(String(20), default="in_progress")  # in_progress, completed
    
    # 对话历史（JSON 存储）
    conversation = Column(JSON, default=list)
    
    # 评价结果
    evaluation = Column(JSON, nullable=True)
    
    # 时间记录
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

