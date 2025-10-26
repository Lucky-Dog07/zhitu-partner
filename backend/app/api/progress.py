from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..api.deps import get_current_user
from ..models.user import User
from ..models.learning_progress import LearningProgress
from ..schemas.progress import ProgressUpdate, ProgressResponse, ProgressStats

router = APIRouter(prefix="/api/progress", tags=["学习进度"])


@router.post("/mark", response_model=ProgressResponse)
async def mark_progress(
    progress_data: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记学习进度"""
    # 查找是否已存在
    existing = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id,
        LearningProgress.learning_path_id == progress_data.learning_path_id,
        LearningProgress.content_id == progress_data.content_id
    ).first()
    
    if existing:
        # 更新已有记录
        if progress_data.mastered is not None:
            existing.mastered = progress_data.mastered
        if progress_data.needs_review is not None:
            existing.needs_review = progress_data.needs_review
        db.commit()
        db.refresh(existing)
        return ProgressResponse.model_validate(existing)
    else:
        # 创建新记录
        progress = LearningProgress(
            user_id=current_user.id,
            learning_path_id=progress_data.learning_path_id,
            content_id=progress_data.content_id,
            content_type=progress_data.content_type,
            mastered=progress_data.mastered or False,
            needs_review=progress_data.needs_review or False
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
        return ProgressResponse.model_validate(progress)


@router.get("/stats", response_model=ProgressStats)
async def get_progress_stats(
    learning_path_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取学习统计"""
    query = db.query(LearningProgress).filter(
        LearningProgress.user_id == current_user.id
    )
    
    if learning_path_id:
        query = query.filter(LearningProgress.learning_path_id == learning_path_id)
    
    total_items = query.count()
    mastered_items = query.filter(LearningProgress.mastered == True).count()
    review_items = query.filter(LearningProgress.needs_review == True).count()
    
    mastery_rate = (mastered_items / total_items * 100) if total_items > 0 else 0.0
    
    return ProgressStats(
        total_items=total_items,
        mastered_items=mastered_items,
        review_items=review_items,
        mastery_rate=round(mastery_rate, 2)
    )

