"""
管理后台 - 登录日志API
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, List
from datetime import datetime, timedelta

from ...core.database import get_db
from ...api.deps import get_current_admin
from ...models.login_log import LoginLog
from ...models.user import User
from pydantic import BaseModel


router = APIRouter()


# Schemas
class LoginLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    username: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    status: str
    fail_reason: Optional[str]
    login_time: datetime
    
    class Config:
        from_attributes = True


class LoginLogListResponse(BaseModel):
    total: int
    logs: List[LoginLogResponse]


class LoginLogStatistics(BaseModel):
    today_logins: int
    today_success: int
    today_failed: int
    success_rate: float
    unique_users_today: int
    suspicious_ips: List[dict]


@router.get("/login-logs", response_model=LoginLogListResponse)
async def list_login_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    username: Optional[str] = None,
    status: Optional[str] = None,
    ip_address: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取登录日志列表"""
    
    # 构建查询
    query = db.query(LoginLog)
    
    # 应用筛选条件
    filters = []
    if username:
        filters.append(LoginLog.username.like(f"%{username}%"))
    if status:
        filters.append(LoginLog.status == status)
    if ip_address:
        filters.append(LoginLog.ip_address.like(f"%{ip_address}%"))
    if start_date:
        filters.append(LoginLog.login_time >= start_date)
    if end_date:
        filters.append(LoginLog.login_time <= end_date)
        
    if filters:
        query = query.filter(and_(*filters))
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    logs = query.order_by(LoginLog.login_time.desc())\
                 .offset(skip)\
                 .limit(limit)\
                 .all()
    
    return LoginLogListResponse(total=total, logs=logs)


@router.get("/login-logs/statistics", response_model=LoginLogStatistics)
async def get_login_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取登录统计"""
    
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 今日登录次数
    today_logins = db.query(func.count(LoginLog.id))\
        .filter(LoginLog.login_time >= today_start)\
        .scalar()
    
    # 今日成功登录
    today_success = db.query(func.count(LoginLog.id))\
        .filter(
            and_(
                LoginLog.login_time >= today_start,
                LoginLog.status == 'success'
            )
        ).scalar()
    
    # 今日失败登录
    today_failed = db.query(func.count(LoginLog.id))\
        .filter(
            and_(
                LoginLog.login_time >= today_start,
                LoginLog.status == 'failed'
            )
        ).scalar()
    
    # 成功率
    success_rate = (today_success / today_logins * 100) if today_logins > 0 else 0
    
    # 今日独立用户数
    unique_users_today = db.query(func.count(func.distinct(LoginLog.user_id)))\
        .filter(
            and_(
                LoginLog.login_time >= today_start,
                LoginLog.status == 'success'
            )
        ).scalar()
    
    # 可疑IP（今日失败次数>=5次）
    suspicious_ips_query = db.query(
        LoginLog.ip_address,
        func.count(LoginLog.id).label('fail_count')
    ).filter(
        and_(
            LoginLog.login_time >= today_start,
            LoginLog.status == 'failed',
            LoginLog.ip_address.isnot(None)
        )
    ).group_by(LoginLog.ip_address)\
     .having(func.count(LoginLog.id) >= 5)\
     .all()
    
    suspicious_ips = [
        {"ip_address": ip, "fail_count": count}
        for ip, count in suspicious_ips_query
    ]
    
    return LoginLogStatistics(
        today_logins=today_logins or 0,
        today_success=today_success or 0,
        today_failed=today_failed or 0,
        success_rate=round(success_rate, 2),
        unique_users_today=unique_users_today or 0,
        suspicious_ips=suspicious_ips
    )


@router.get("/login-logs/user/{user_id}", response_model=LoginLogListResponse)
async def get_user_login_logs(
    user_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取指定用户的登录历史"""
    
    logs = db.query(LoginLog)\
        .filter(LoginLog.user_id == user_id)\
        .order_by(LoginLog.login_time.desc())\
        .limit(limit)\
        .all()
    
    total = db.query(func.count(LoginLog.id))\
        .filter(LoginLog.user_id == user_id)\
        .scalar()
    
    return LoginLogListResponse(total=total or 0, logs=logs)

