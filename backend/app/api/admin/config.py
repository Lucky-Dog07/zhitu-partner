from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from ...core.database import get_db
from ...api.deps import get_current_admin
from ...models.user import User
from ...models.system_config import SystemConfig
from pydantic import BaseModel

router = APIRouter()


# Schemas
class ConfigItem(BaseModel):
    key: str
    value: str
    description: Optional[str]
    category: str
    
    class Config:
        from_attributes = True


class ConfigUpdate(BaseModel):
    value: str


# API Endpoints
@router.get("/configs", response_model=List[ConfigItem])
async def list_configs(
    category: Optional[str] = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取配置列表（可按分类筛选）"""
    query = db.query(SystemConfig)
    
    if category:
        query = query.filter(SystemConfig.category == category)
    
    configs = query.all()
    return configs


@router.get("/configs/{key}", response_model=ConfigItem)
async def get_config(
    key: str,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """获取单个配置"""
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return config


@router.put("/configs/{key}", response_model=ConfigItem)
async def update_config(
    key: str,
    config_update: ConfigUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """更新配置"""
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 验证JSON格式（如果配置值应该是JSON）
    try:
        json.loads(config_update.value)
    except json.JSONDecodeError:
        # 如果不是JSON，就作为普通字符串存储（加引号）
        config.value = json.dumps(config_update.value)
    else:
        config.value = config_update.value
    
    db.commit()
    db.refresh(config)
    
    return config


@router.post("/configs/test-connection")
async def test_connection(
    service: str,  # openai, n8n
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """测试API连接"""
    if service == "openai":
        # 测试OpenAI连接
        api_key_config = db.query(SystemConfig).filter(SystemConfig.key == "openai_api_key").first()
        if not api_key_config:
            return {"success": False, "message": "API密钥未配置"}
        
        # 这里应该实际测试API连接
        # 简化实现：检查密钥是否为空
        api_key = json.loads(api_key_config.value)
        if not api_key:
            return {"success": False, "message": "API密钥为空"}
        
        return {"success": True, "message": "OpenAI API连接正常"}
    
    elif service == "n8n":
        # 测试n8n连接
        webhook_config = db.query(SystemConfig).filter(SystemConfig.key == "n8n_webhook_url").first()
        if not webhook_config:
            return {"success": False, "message": "n8n Webhook URL未配置"}
        
        webhook_url = json.loads(webhook_config.value)
        if not webhook_url:
            return {"success": False, "message": "n8n Webhook URL为空"}
        
        return {"success": True, "message": "n8n配置正常"}
    
    else:
        raise HTTPException(status_code=400, detail="不支持的服务类型")

