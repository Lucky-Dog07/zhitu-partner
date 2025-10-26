from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notebook_id = Column(Integer, ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=True)  # 关联笔记本
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id", ondelete="SET NULL"), nullable=True)  # 可选关联学习路径
    title = Column(String(200))
    content = Column(Text, nullable=False)
    tags = Column(JSON, default=list)  # JSON类型，兼容SQLite和PostgreSQL
    editor_mode = Column(String(20), default="markdown")  # markdown 或 rich_text
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="notes")

