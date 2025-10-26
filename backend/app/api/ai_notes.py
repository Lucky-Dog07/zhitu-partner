from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..api.deps import get_current_user
from ..models.user import User
from ..schemas.ai_note import (
    NoteGenerationRequest,
    NoteDraftResponse,
    NoteDraftMetadata
)
from ..services.ai_note_generator import AINoteGenerator

router = APIRouter()


@router.post("/generate-draft", response_model=NoteDraftResponse)
async def generate_note_draft(
    request: NoteGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成 AI 笔记草稿
    
    根据用户选择的数据源（错题/面试题/学习路径）和选项，
    AI 生成个性化的学习笔记草稿
    
    请求体示例：
    ```json
    {
        "source_type": "mistakes",
        "source_id": 123,
        "options": {
            "include_weak_points": true,
            "include_study_plan": true,
            "include_interview_tips": true,
            "custom_requirements": "重点分析算法题"
        }
    }
    ```
    """
    try:
        generator = AINoteGenerator(db)
        
        # 根据数据源类型调用不同的生成方法
        if request.source_type == "mistakes":
            draft_data = await generator.generate_from_mistakes(
                user_id=current_user.id,
                learning_path_id=request.source_id,
                include_weak_points=request.options.include_weak_points,
                include_study_plan=request.options.include_study_plan,
                include_interview_tips=request.options.include_interview_tips,
                custom_requirements=request.options.custom_requirements
            )
        elif request.source_type == "interview":
            draft_data = await generator.generate_from_interview_questions(
                user_id=current_user.id,
                learning_path_id=request.source_id,
                include_weak_points=request.options.include_weak_points,
                include_study_plan=request.options.include_study_plan,
                include_interview_tips=request.options.include_interview_tips,
                custom_requirements=request.options.custom_requirements
            )
        elif request.source_type == "learning_path":
            draft_data = await generator.generate_from_learning_path(
                user_id=current_user.id,
                learning_path_id=request.source_id,
                include_weak_points=request.options.include_weak_points,
                include_study_plan=request.options.include_study_plan,
                include_interview_tips=request.options.include_interview_tips,
                custom_requirements=request.options.custom_requirements
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的数据源类型: {request.source_type}"
            )
        
        # 构建响应
        response = NoteDraftResponse(
            title=draft_data['title'],
            content=draft_data['content'],
            suggested_notebook=draft_data['suggested_notebook'],
            metadata=NoteDraftMetadata(**draft_data['metadata'])
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成笔记失败: {str(e)}"
        )

