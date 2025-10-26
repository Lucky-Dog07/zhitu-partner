from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class LearningProgress(Base):
    __tablename__ = "learning_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False)
    content_id = Column(String(200), nullable=False)  # 内容标识符
    content_type = Column(String(50), nullable=False)  # mindmap, knowledge, interview等
    mastered = Column(Boolean, default=False)  # 是否已掌握
    needs_review = Column(Boolean, default=False)  # 是否需要复习
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="learning_progress")
    learning_path = relationship("LearningPath", back_populates="progress")

