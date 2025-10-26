from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum


class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100))  # 技术基础/项目经验/行为面试等，由AI灵活生成
    difficulty = Column(String(20), default="medium")
    knowledge_points = Column(JSON)  # 关联的知识点列表
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    learning_path = relationship("LearningPath", back_populates="interview_questions")
    statuses = relationship("QuestionStatus", back_populates="question", cascade="all, delete-orphan")

