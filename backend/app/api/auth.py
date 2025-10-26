from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime
from ..core.database import get_db
from ..core.security import verify_password, get_password_hash, create_access_token
from ..models.user import User
from ..models.login_log import LoginLog
from ..schemas.user import UserCreate, UserLogin, Token, UserResponse
from ..services.notebook_service import init_default_notebooks

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建用户
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 为新用户创建默认笔记本
    init_default_notebooks(db, user.id)
    
    # 生成令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """用户登录"""
    # 获取客户端信息
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")
    
    # 查找用户
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        # 记录登录失败日志
        login_log = LoginLog(
            user_id=user.id if user else None,
            username=credentials.username,
            ip_address=ip_address,
            user_agent=user_agent,
            status="failed",
            fail_reason="用户名或密码错误"
        )
        db.add(login_log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查账号是否被禁用
    if not user.is_active:
        # 记录登录失败日志
        login_log = LoginLog(
            user_id=user.id,
            username=credentials.username,
            ip_address=ip_address,
            user_agent=user_agent,
            status="failed",
            fail_reason="账号已被禁用"
        )
        db.add(login_log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )
    
    # 更新最后登录时间
    user.last_login_at = func.now()
    
    # 记录成功登录日志
    login_log = LoginLog(
        user_id=user.id,
        username=credentials.username,
        ip_address=ip_address,
        user_agent=user_agent,
        status="success"
    )
    db.add(login_log)
    db.commit()
    db.refresh(user)
    
    # 生成令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )

