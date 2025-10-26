from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..api.deps import get_current_user
from ..models.user import User
from ..models.note import Note
from ..schemas.note import NoteCreate, NoteUpdate, NoteResponse

router = APIRouter(prefix="/api/notes", tags=["笔记"])


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建笔记"""
    note = Note(
        user_id=current_user.id,
        notebook_id=note_data.notebook_id,
        title=note_data.title,
        content=note_data.content,
        tags=note_data.tags,
        editor_mode=note_data.editor_mode,
        learning_path_id=note_data.learning_path_id
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    
    return NoteResponse.model_validate(note)


@router.get("", response_model=List[NoteResponse])
async def list_notes(
    skip: int = 0,
    limit: int = 50,
    tag: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取笔记列表"""
    query = db.query(Note).filter(Note.user_id == current_user.id)
    
    # 按标签筛选
    if tag:
        query = query.filter(Note.tags.contains([tag]))
    
    notes = query.order_by(Note.updated_at.desc()).offset(skip).limit(limit).all()
    
    return [NoteResponse.model_validate(note) for note in notes]


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个笔记"""
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在"
        )
    
    return NoteResponse.model_validate(note)


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新笔记"""
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在"
        )
    
    # 更新字段
    if note_data.title is not None:
        note.title = note_data.title
    if note_data.content is not None:
        note.content = note_data.content
    if note_data.tags is not None:
        note.tags = note_data.tags
    
    db.commit()
    db.refresh(note)
    
    return NoteResponse.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除笔记"""
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="笔记不存在"
        )
    
    db.delete(note)
    db.commit()

