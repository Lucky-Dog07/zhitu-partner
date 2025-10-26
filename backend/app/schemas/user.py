from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """用户注册"""
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """用户登录"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    role: str = "user"
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT令牌"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

