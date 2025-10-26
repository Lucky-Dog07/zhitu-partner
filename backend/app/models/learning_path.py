from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class LearningPath(Base):
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    position = Column(String(200), nullable=False)
    job_description = Column(Text)
    generated_content = Column(JSON)  # 存储完整的AI生成内容
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="learning_paths")
    progress = relationship("LearningProgress", back_populates="learning_path", cascade="all, delete-orphan")
    interview_questions = relationship("InterviewQuestion", back_populates="learning_path", cascade="all, delete-orphan")

