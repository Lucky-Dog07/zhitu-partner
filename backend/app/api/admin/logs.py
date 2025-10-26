"""
管理后台 - 操作日志API
"""
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List
from datetime import datetime, timedelta
import csv
import io

from ...core.database import get_db
from ...api.deps import get_current_admin
from ...models.operation_log import OperationLog
from ...models.user import User
from pydantic import BaseModel


router = APIRouter()


# Schemas
class OperationLogResponse(BaseModel):
    id: int
    admin_id: int
    username: str
    action: str
    target_type: Optional[str]
    target_id: Optional[int]
    details: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class OperationLogListResponse(BaseModel):
    total: int
    logs: List[OperationLogResponse]


@router.get("/logs", response_model=OperationLogListResponse)
async def list_operation_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取操作日志列表（支持筛选）"""
    
    # 构建查询
    query = db.query(OperationLog).join(User, OperationLog.admin_id == User.id)
    
    # 应用筛选条件
    filters = []
    if action:
        filters.append(OperationLog.action.like(f"%{action}%"))
    if target_type:
        filters.append(OperationLog.target_type == target_type)
    if user_id:
        filters.append(OperationLog.admin_id == user_id)
    if start_date:
        filters.append(OperationLog.created_at >= start_date)
    if end_date:
        filters.append(OperationLog.created_at <= end_date)
        
    if filters:
        query = query.filter(and_(*filters))
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    logs = query.order_by(OperationLog.created_at.desc())\
                 .offset(skip)\
                 .limit(limit)\
                 .all()
    
    # 添加用户名
    log_responses = []
    for log in logs:
        # 获取关联的admin用户
        admin_user = db.query(User).filter(User.id == log.admin_id).first()
        log_dict = {
            "id": log.id,
            "admin_id": log.admin_id,
            "username": admin_user.username if admin_user else "Unknown",
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "details": str(log.details) if log.details else None,
            "ip_address": log.ip_address,
            "created_at": log.created_at
        }
        log_responses.append(OperationLogResponse(**log_dict))
    
    return OperationLogListResponse(total=total, logs=log_responses)


@router.get("/logs/{log_id}", response_model=OperationLogResponse)
async def get_operation_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取单个操作日志详情"""
    
    log = db.query(OperationLog).filter(OperationLog.id == log_id).first()
    if not log:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="日志不存在")
    
    admin_user = db.query(User).filter(User.id == log.admin_id).first()
    log_dict = {
        "id": log.id,
        "admin_id": log.admin_id,
        "username": admin_user.username if admin_user else "Unknown",
        "action": log.action,
        "target_type": log.target_type,
        "target_id": log.target_id,
        "details": str(log.details) if log.details else None,
        "ip_address": log.ip_address,
        "created_at": log.created_at
    }
    
    return OperationLogResponse(**log_dict)


@router.get("/logs/export/csv")
async def export_logs_csv(
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """导出操作日志为CSV"""
    
    # 构建查询
    query = db.query(OperationLog).join(User, OperationLog.admin_id == User.id)
    
    # 应用筛选条件
    filters = []
    if action:
        filters.append(OperationLog.action.like(f"%{action}%"))
    if target_type:
        filters.append(OperationLog.target_type == target_type)
    if user_id:
        filters.append(OperationLog.admin_id == user_id)
    if start_date:
        filters.append(OperationLog.created_at >= start_date)
    if end_date:
        filters.append(OperationLog.created_at <= end_date)
        
    if filters:
        query = query.filter(and_(*filters))
    
    logs = query.order_by(OperationLog.created_at.desc()).limit(10000).all()
    
    # 创建CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow(['ID', '管理员ID', '用户名', '操作', '目标类型', '目标ID', 'IP地址', '时间'])
    
    # 写入数据
    for log in logs:
        admin_user = db.query(User).filter(User.id == log.admin_id).first()
        writer.writerow([
            log.id,
            log.admin_id,
            admin_user.username if admin_user else "Unknown",
            log.action,
            log.target_type or '',
            log.target_id or '',
            log.ip_address or '',
            log.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # 返回CSV文件
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=operation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )


@router.get("/logs/stats/summary")
async def get_logs_summary(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取操作日志统计摘要"""
    
    start_date = datetime.now() - timedelta(days=days)
    
    # 总操作数
    total_operations = db.query(func.count(OperationLog.id))\
        .filter(OperationLog.created_at >= start_date)\
        .scalar()
    
    # 操作类型分布
    action_distribution = db.query(
        OperationLog.action,
        func.count(OperationLog.id).label('count')
    ).filter(OperationLog.created_at >= start_date)\
     .group_by(OperationLog.action)\
     .all()
    
    # 活跃管理员
    active_admins = db.query(
        User.username,
        func.count(OperationLog.id).label('operation_count')
    ).join(OperationLog, User.id == OperationLog.admin_id)\
     .filter(OperationLog.created_at >= start_date)\
     .group_by(User.id, User.username)\
     .order_by(func.count(OperationLog.id).desc())\
     .limit(5)\
     .all()
    
    return {
        "total_operations": total_operations,
        "action_distribution": [
            {"action": action, "count": count}
            for action, count in action_distribution
        ],
        "active_admins": [
            {"username": username, "operation_count": count}
            for username, count in active_admins
        ],
        "period_days": days
    }
