from sqlalchemy.orm import Session
from ..models.notebook import Notebook


# 默认笔记本配置
DEFAULT_NOTEBOOKS = [
    {"name": "面试笔记", "description": "记录面试题目和解析", "icon": "📚", "is_default": True},
    {"name": "错题本", "description": "记录错题和薄弱知识点", "icon": "📝", "is_default": True},
    {"name": "学习笔记", "description": "记录学习路线和知识点", "icon": "📖", "is_default": True},
    {"name": "日常笔记", "description": "记录日常想法和总结", "icon": "📅", "is_default": True},
]


def init_default_notebooks(db: Session, user_id: int) -> list[Notebook]:
    """
    为新用户创建默认笔记本
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        创建的笔记本列表
    """
    notebooks = []
    
    for notebook_data in DEFAULT_NOTEBOOKS:
        # 检查是否已存在
        existing = db.query(Notebook).filter(
            Notebook.user_id == user_id,
            Notebook.name == notebook_data["name"]
        ).first()
        
        if not existing:
            notebook = Notebook(
                user_id=user_id,
                **notebook_data
            )
            db.add(notebook)
            notebooks.append(notebook)
    
    db.commit()
    return notebooks


def get_default_notebook(db: Session, user_id: int, notebook_name: str = "日常笔记") -> Notebook:
    """
    获取用户的默认笔记本
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        notebook_name: 笔记本名称
        
    Returns:
        笔记本对象
    """
    notebook = db.query(Notebook).filter(
        Notebook.user_id == user_id,
        Notebook.name == notebook_name,
        Notebook.is_default == True
    ).first()
    
    if not notebook:
        # 如果不存在，创建默认笔记本
        init_default_notebooks(db, user_id)
        notebook = db.query(Notebook).filter(
            Notebook.user_id == user_id,
            Notebook.name == notebook_name
        ).first()
    
    return notebook

