from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..core.database import get_db
from ..api.deps import get_current_user
from ..models.user import User
from ..models.notebook import Notebook
from ..models.note import Note
from ..schemas.notebook import NotebookCreate, NotebookUpdate, NotebookResponse
from ..services.notebook_service import init_default_notebooks

router = APIRouter()


@router.get("/", response_model=List[NotebookResponse])
async def get_notebooks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的笔记本列表（包含笔记数量）"""
    # 查询笔记本及笔记数量
    notebooks = db.query(
        Notebook,
        func.count(Note.id).label('note_count')
    ).outerjoin(
        Note, (Note.notebook_id == Notebook.id) & (Note.user_id == current_user.id)
    ).filter(
        Notebook.user_id == current_user.id
    ).group_by(Notebook.id).all()
    
    # 如果没有笔记本，创建默认笔记本
    if not notebooks:
        init_default_notebooks(db, current_user.id)
        notebooks = db.query(
            Notebook,
            func.count(Note.id).label('note_count')
        ).outerjoin(
            Note, (Note.notebook_id == Notebook.id) & (Note.user_id == current_user.id)
        ).filter(
            Notebook.user_id == current_user.id
        ).group_by(Notebook.id).all()
    
    # 构建响应
    result = []
    for notebook, note_count in notebooks:
        notebook_dict = {
            "id": notebook.id,
            "user_id": notebook.user_id,
            "name": notebook.name,
            "description": notebook.description,
            "icon": notebook.icon,
            "is_default": notebook.is_default,
            "note_count": note_count,
            "created_at": notebook.created_at
        }
        result.append(NotebookResponse(**notebook_dict))
    
    return result


@router.post("/", response_model=NotebookResponse)
async def create_notebook(
    notebook_data: NotebookCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建自定义笔记本"""
    notebook = Notebook(
        user_id=current_user.id,
        name=notebook_data.name,
        description=notebook_data.description,
        icon=notebook_data.icon,
        is_default=False
    )
    
    db.add(notebook)
    db.commit()
    db.refresh(notebook)
    
    return NotebookResponse(
        id=notebook.id,
        user_id=notebook.user_id,
        name=notebook.name,
        description=notebook.description,
        icon=notebook.icon,
        is_default=notebook.is_default,
        note_count=0,
        created_at=notebook.created_at
    )


@router.put("/{notebook_id}", response_model=NotebookResponse)
async def update_notebook(
    notebook_id: int,
    notebook_data: NotebookUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新笔记本"""
    notebook = db.query(Notebook).filter(
        Notebook.id == notebook_id,
        Notebook.user_id == current_user.id
    ).first()
    
    if not notebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记本不存在"
        )
    
    # 更新字段
    if notebook_data.name is not None:
        notebook.name = notebook_data.name
    if notebook_data.description is not None:
        notebook.description = notebook_data.description
    if notebook_data.icon is not None:
        notebook.icon = notebook_data.icon
    
    db.commit()
    db.refresh(notebook)
    
    # 获取笔记数量
    note_count = db.query(func.count(Note.id)).filter(
        Note.notebook_id == notebook_id,
        Note.user_id == current_user.id
    ).scalar()
    
    return NotebookResponse(
        id=notebook.id,
        user_id=notebook.user_id,
        name=notebook.name,
        description=notebook.description,
        icon=notebook.icon,
        is_default=notebook.is_default,
        note_count=note_count,
        created_at=notebook.created_at
    )


@router.delete("/{notebook_id}")
async def delete_notebook(
    notebook_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除笔记本（不能删除默认笔记本）"""
    notebook = db.query(Notebook).filter(
        Notebook.id == notebook_id,
        Notebook.user_id == current_user.id
    ).first()
    
    if not notebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记本不存在"
        )
    
    if notebook.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除默认笔记本"
        )
    
    # 将该笔记本下的笔记移动到"日常笔记"
    default_notebook = db.query(Notebook).filter(
        Notebook.user_id == current_user.id,
        Notebook.name == "日常笔记",
        Notebook.is_default == True
    ).first()
    
    if default_notebook:
        db.query(Note).filter(
            Note.notebook_id == notebook_id
        ).update({"notebook_id": default_notebook.id})
    
    db.delete(notebook)
    db.commit()
    
    return {"message": "笔记本删除成功"}

