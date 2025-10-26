from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..core.database import Base


class Notebook(Base):
    """笔记本模型"""
    __tablename__ = "notebooks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    icon = Column(String(50), default="📚")  # emoji 图标
    is_default = Column(Boolean, default=False)  # 是否为默认笔记本
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

