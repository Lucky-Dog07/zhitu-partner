#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import Base, engine
from app.models.user import User
from app.models.learning_path import LearningPath
from app.models.learning_progress import LearningProgress
from app.models.notebook import Notebook
from app.models.note import Note
from app.models.chat_history import ChatHistory
from app.models.interview_question import InterviewQuestion
from app.models.question_status import QuestionStatus

def init_database():
    """初始化数据库，创建所有表"""
    print("正在创建数据库表...")
    
    # 导入所有模型以确保它们被注册
    print(f"注册的模型: {Base.metadata.tables.keys()}")
    
    # 删除所有表（慎用！）
    # Base.metadata.drop_all(bind=engine)
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    print("✅ 数据库表创建成功！")
    print(f"创建的表: {list(Base.metadata.tables.keys())}")

if __name__ == "__main__":
    init_database()

