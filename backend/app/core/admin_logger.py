"""
管理员操作日志装饰器
"""
from functools import wraps
from typing import Optional
from fastapi import Request
from sqlalchemy.orm import Session
from ..models.operation_log import OperationLog
import json


def log_admin_action(action: str, target_type: Optional[str] = None):
    """
    记录管理员操作的装饰器
    
    Args:
        action: 操作类型，如 "create_user", "update_config"
        target_type: 目标类型，如 "User", "SystemConfig"
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 执行原函数
            result = await func(*args, **kwargs)
            
            # 尝试从参数中获取 request, db, current_user
            request: Optional[Request] = None
            db: Optional[Session] = None
            current_user = None
            target_id: Optional[int] = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                elif hasattr(arg, 'query'):  # SQLAlchemy Session
                    db = arg
                    
            # 从kwargs中获取
            if 'request' in kwargs:
                request = kwargs['request']
            if 'db' in kwargs:
                db = kwargs['db']
            if 'current_user' in kwargs:
                current_user = kwargs['current_user']
                
            # 尝试从路径参数中获取target_id
            if 'id' in kwargs:
                target_id = kwargs['id']
            elif 'user_id' in kwargs:
                target_id = kwargs['user_id']
            elif 'config_id' in kwargs:
                target_id = kwargs['config_id']
                
            # 记录日志
            if db and current_user:
                try:
                    # 获取IP地址
                    ip_address = None
                    if request:
                        ip_address = request.client.host if request.client else None
                        
                    # 构建详情（简化版，避免敏感信息）
                    details = {
                        "action": action,
                        "target_type": target_type,
                        "target_id": target_id,
                    }
                    
                    log_entry = OperationLog(
                        user_id=current_user.id,
                        action=action,
                        target_type=target_type,
                        target_id=target_id,
                        details=json.dumps(details),
                        ip_address=ip_address
                    )
                    db.add(log_entry)
                    db.commit()
                except Exception as e:
                    # 日志记录失败不应影响主业务
                    print(f"Failed to log admin action: {e}")
                    
            return result
        return wrapper
    return decorator

