"""
登录日志模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class LoginLog(Base):
    """登录日志"""
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 登录失败时可能为空
    username = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False)  # success, failed
    fail_reason = Column(String(200), nullable=True)
    
    login_time = Column(DateTime(timezone=True), server_default=func.now())

    # 关联关系
    user = relationship("User", foreign_keys=[user_id])

