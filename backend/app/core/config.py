from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "职途伴侣 API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./zhitu.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    # n8n配置
    N8N_BASE_URL: str = "http://localhost:5678"
    N8N_WEBHOOK_PATH: str = "/webhook/zhitu-learning"
    
    # OpenAI配置
    OPENAI_API_KEY: str = "sk-e9uTDJ84fQ8uUnfbTuItZ6wmGaOzsKyO7XudRwyH4Tw2aitt"
    OPENAI_BASE_URL: str = "https://api.qingyuntop.top/v1"
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

