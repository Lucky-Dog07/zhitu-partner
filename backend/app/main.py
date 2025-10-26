from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import engine, Base
from .api import auth, learning_paths, progress, notes, notebooks, chat, tech_links, interview, ai_assistant, ai_notes, interview_simulator
from .api.admin import users as admin_users, analytics as admin_analytics, config as admin_config, logs as admin_logs, login_logs as admin_login_logs, dashboard as admin_dashboard

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="职途伴侣 - AI驱动的职业技能提升助手"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(learning_paths.router)
app.include_router(progress.router)
app.include_router(notes.router)
app.include_router(notebooks.router, prefix="/api/notebooks", tags=["笔记本"])
app.include_router(chat.router)
app.include_router(tech_links.router)
app.include_router(interview.router)
app.include_router(ai_assistant.router, prefix="/api/ai-assistant", tags=["AI助手"])
app.include_router(ai_notes.router, prefix="/api/ai-notes", tags=["AI笔记"])
app.include_router(interview_simulator.router, prefix="/api/interview-simulator", tags=["面试模拟"])

# 管理后台路由
app.include_router(admin_dashboard.router, prefix="/api/admin", tags=["管理-仪表盘"])
app.include_router(admin_users.router, prefix="/api/admin", tags=["管理-用户"])
app.include_router(admin_analytics.router, prefix="/api/admin", tags=["管理-数据统计"])
app.include_router(admin_config.router, prefix="/api/admin", tags=["管理-系统配置"])
app.include_router(admin_logs.router, prefix="/api/admin", tags=["管理-操作日志"])
app.include_router(admin_login_logs.router, prefix="/api/admin", tags=["管理-登录日志"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

