from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class QuestionStatusEnum(str, enum.Enum):
    NOT_SEEN = "not_seen"
    MASTERED = "mastered"
    NOT_MASTERED = "not_mastered"


class QuestionStatus(Base):
    __tablename__ = "question_statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="not_seen", nullable=False)
    last_reviewed_at = Column(DateTime(timezone=True))
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="question_statuses")
    question = relationship("InterviewQuestion", back_populates="statuses")
    
    # 唯一约束：每个用户对每道题只能有一个状态记录
    __table_args__ = (
        UniqueConstraint('user_id', 'question_id', name='uq_user_question'),
    )

