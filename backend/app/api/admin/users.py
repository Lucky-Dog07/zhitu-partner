from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from datetime import datetime, timedelta
from ...core.database import get_db
from ...api.deps import get_current_admin
from ...models.user import User
from ...models.learning_path import LearningPath
from ...models.note import Note
from ...models.interview_question import InterviewQuestion
from ...models.operation_log import OperationLog
from pydantic import BaseModel, EmailStr

router = APIRouter()


def log_operation(db: Session, admin: User, action: str, target_type: str, target_id: int, request: Request, details: dict = None):
    """记录操作日志的辅助函数"""
    try:
        log = OperationLog(
            admin_id=admin.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=request.client.host if request.client else None
        )
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"Failed to log operation: {e}")
        # 不影响主操作


# Schemas
class UserListItem(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    learning_paths_count: int
    notes_count: int
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    total: int
    items: List[UserListItem]


class UserDetail(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login_at: Optional[datetime]
    learning_paths_count: int
    notes_count: int
    interview_questions_count: int
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None


class UserStatusUpdate(BaseModel):
    is_active: bool


# API Endpoints
@router.get("/users", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取用户列表（分页、搜索、筛选）"""
    query = db.query(User)
    
    # 搜索
    if search:
        query = query.filter(
            or_(
                User.username.like(f"%{search}%"),
                User.email.like(f"%{search}%")
            )
        )
    
    # 角色筛选
    if role:
        query = query.filter(User.role == role)
    
    # 状态筛选
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    # 构造响应
    items = []
    for user in users:
        learning_paths_count = db.query(func.count(LearningPath.id)).filter(LearningPath.user_id == user.id).scalar()
        notes_count = db.query(func.count(Note.id)).filter(Note.user_id == user.id).scalar()
        
        items.append(UserListItem(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
            learning_paths_count=learning_paths_count,
            notes_count=notes_count
        ))
    
    return UserListResponse(total=total, items=items)


@router.get("/users/{user_id}", response_model=UserDetail)
async def get_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 统计数据
    learning_paths_count = db.query(func.count(LearningPath.id)).filter(LearningPath.user_id == user.id).scalar()
    notes_count = db.query(func.count(Note.id)).filter(Note.user_id == user.id).scalar()
    interview_questions_count = db.query(func.count(InterviewQuestion.id)).filter(InterviewQuestion.learning_path_id.in_(
        db.query(LearningPath.id).filter(LearningPath.user_id == user.id)
    )).scalar()
    
    return UserDetail(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        learning_paths_count=learning_paths_count,
        notes_count=notes_count,
        interview_questions_count=interview_questions_count
    )


@router.put("/users/{user_id}", response_model=UserDetail)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新字段
    if user_update.username is not None:
        # 检查用户名是否已存在
        existing = db.query(User).filter(User.username == user_update.username, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="用户名已存在")
        user.username = user_update.username
    
    if user_update.email is not None:
        # 检查邮箱是否已存在
        existing = db.query(User).filter(User.email == user_update.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="邮箱已存在")
        user.email = user_update.email
    
    if user_update.role is not None:
        if user_update.role not in ["user", "admin"]:
            raise HTTPException(status_code=400, detail="无效的角色")
        user.role = user_update.role
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # 返回更新后的用户详情
    return await get_user(user_id, admin, db)


@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """启用/禁用用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不能禁用自己
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="不能禁用自己的账号")
    
    user.is_active = status_update.is_active
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "用户状态更新成功", "is_active": user.is_active}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不能删除自己
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")
    
    # 不能删除其他管理员
    if user.role == "admin":
        raise HTTPException(status_code=400, detail="不能删除管理员账号")
    
    db.delete(user)
    db.commit()
    
    return {"message": "用户删除成功"}


@router.get("/users/{user_id}/statistics")
async def get_user_statistics(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取用户数据统计"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 学习路线统计
    learning_paths_count = db.query(func.count(LearningPath.id)).filter(LearningPath.user_id == user.id).scalar()
    
    # 笔记统计
    notes_count = db.query(func.count(Note.id)).filter(Note.user_id == user.id).scalar()
    
    # 面试题统计
    learning_path_ids = db.query(LearningPath.id).filter(LearningPath.user_id == user.id).subquery()
    interview_questions_count = db.query(func.count(InterviewQuestion.id)).filter(
        InterviewQuestion.learning_path_id.in_(learning_path_ids)
    ).scalar()
    
    # 最近7天活跃度（这里简化，实际需要记录用户活动日志）
    recent_active = user.last_login_at and (datetime.utcnow() - user.last_login_at) < timedelta(days=7)
    
    return {
        "user_id": user.id,
        "username": user.username,
        "learning_paths_count": learning_paths_count,
        "notes_count": notes_count,
        "interview_questions_count": interview_questions_count,
        "is_recently_active": recent_active,
        "created_at": user.created_at,
        "last_login_at": user.last_login_at
    }

