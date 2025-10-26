from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import List, Optional
from datetime import datetime
from ..core.database import get_db
from ..api.deps import get_current_user
from ..models.user import User
from ..models.interview_question import InterviewQuestion
from ..models.question_status import QuestionStatus
from ..models.learning_path import LearningPath
from ..schemas.interview import (
    InterviewQuestionGenerate,
    InterviewQuestionResponse,
    InterviewQuestionsListResponse,
    InterviewStatistics,
    QuestionStatusUpdate,
    GenerateQuestionsResponse
)
from ..services.interview_service import interview_service

router = APIRouter(prefix="/api/interview", tags=["面试题库"])


@router.post("/generate", response_model=GenerateQuestionsResponse)
async def generate_questions(
    request: InterviewQuestionGenerate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成面试题"""
    # 验证学习路线权限
    learning_path = db.query(LearningPath).filter(
        LearningPath.id == request.learning_path_id,
        LearningPath.user_id == current_user.id
    ).first()
    
    if not learning_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路线不存在"
        )
    
    try:
        # 生成题目
        questions = await interview_service.generate_questions(
            db=db,
            learning_path_id=request.learning_path_id,
            count=request.count,
            category=request.category,
            based_on_weak_points=request.based_on_weak_points
        )
        
        # 转换为响应格式
        question_responses = []
        for q in questions:
            question_responses.append(InterviewQuestionResponse(
                id=q.id,
                learning_path_id=q.learning_path_id,
                question=q.question,
                answer=q.answer,
                category=q.category,
                difficulty=q.difficulty,
                knowledge_points=q.knowledge_points,
                created_at=q.created_at,
                user_status="not_seen",
                review_count=0
            ))
        
        return GenerateQuestionsResponse(
            success=True,
            message=f"成功生成{len(questions)}道面试题",
            questions=question_responses,
            count=len(questions)
        )
        
    except Exception as e:
        print(f"[ERROR] 生成题目失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成题目失败: {str(e)}"
        )


@router.get("/questions/all/mistakes", response_model=InterviewQuestionsListResponse)
async def get_all_mistakes(
    limit: int = Query(500, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户所有学习路线的错题"""
    # 查询所有用户的学习路线
    user_learning_paths = db.query(LearningPath).filter(
        LearningPath.user_id == current_user.id
    ).all()
    
    if not user_learning_paths:
        # 空统计数据
        empty_stats = InterviewStatistics(
            total=0,
            not_seen=0,
            mastered=0,
            not_mastered=0,
            mastery_rate=0.0,
            weak_categories=[],
            weak_knowledge_points=[]
        )
        return InterviewQuestionsListResponse(
            questions=[],
            statistics=empty_stats,
            total=0,
            has_more=False
        )
    
    # 获取所有学习路线的ID
    path_ids = [path.id for path in user_learning_paths]
    
    # 获取所有题目（用于统计）
    all_questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.learning_path_id.in_(path_ids)
    ).all()
    
    # 获取所有状态记录
    all_question_ids = [q.id for q in all_questions]
    all_statuses = db.query(QuestionStatus).filter(
        QuestionStatus.question_id.in_(all_question_ids),
        QuestionStatus.user_id == current_user.id
    ).all()
    
    # 构建状态映射
    all_status_map = {s.question_id: s for s in all_statuses}
    
    # 计算统计信息
    stats = {
        'total': len(all_questions),
        'not_seen': 0,
        'mastered': 0,
        'not_mastered': 0
    }
    
    category_count = {}
    knowledge_point_count = {}
    
    for q in all_questions:
        status_obj = all_status_map.get(q.id)
        if status_obj:
            if status_obj.status == 'not_seen':
                stats['not_seen'] += 1
            elif status_obj.status == 'mastered':
                stats['mastered'] += 1
            elif status_obj.status == 'not_mastered':
                stats['not_mastered'] += 1
                # 统计薄弱分类
                category_count[q.category] = category_count.get(q.category, 0) + 1
                # 统计薄弱知识点
                for kp in q.knowledge_points:
                    knowledge_point_count[kp] = knowledge_point_count.get(kp, 0) + 1
        else:
            stats['not_seen'] += 1
    
    # 计算掌握率
    mastery_rate = stats['mastered'] / stats['total'] if stats['total'] > 0 else 0.0
    
    # 构建薄弱分类和知识点列表
    weak_categories = [
        {"category": cat, "count": count}
        for cat, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    weak_knowledge_points = [
        {"point": kp, "count": count}
        for kp, count in sorted(knowledge_point_count.items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    
    statistics = InterviewStatistics(
        total=stats['total'],
        not_seen=stats['not_seen'],
        mastered=stats['mastered'],
        not_mastered=stats['not_mastered'],
        mastery_rate=mastery_rate,
        weak_categories=weak_categories,
        weak_knowledge_points=weak_knowledge_points
    )
    
    # 构建查询：所有学习路线的错题
    query = db.query(InterviewQuestion).filter(
        InterviewQuestion.learning_path_id.in_(path_ids)
    ).join(
        QuestionStatus,
        (QuestionStatus.question_id == InterviewQuestion.id) &
        (QuestionStatus.user_id == current_user.id)
    ).filter(QuestionStatus.status == "not_mastered")
    
    # 总数
    total = query.count()
    
    # 分页
    questions = query.offset(offset).limit(limit).all()
    
    # 获取用户状态
    question_ids = [q.id for q in questions]
    statuses = db.query(QuestionStatus).filter(
        QuestionStatus.question_id.in_(question_ids),
        QuestionStatus.user_id == current_user.id
    ).all()
    
    status_map = {s.question_id: s for s in statuses}
    
    # 转换为响应格式
    question_responses = []
    for q in questions:
        user_status_obj = status_map.get(q.id)
        question_responses.append(InterviewQuestionResponse(
            id=q.id,
            learning_path_id=q.learning_path_id,
            question=q.question,
            answer=q.answer,
            category=q.category,
            difficulty=q.difficulty,
            knowledge_points=q.knowledge_points,
            created_at=q.created_at,
            user_status=user_status_obj.status if user_status_obj else "not_seen",
            review_count=user_status_obj.review_count if user_status_obj else 0
        ))
    
    return InterviewQuestionsListResponse(
        questions=question_responses,
        statistics=statistics,
        total=total,
        has_more=(offset + limit) < total
    )


@router.get("/questions/{learning_path_id}", response_model=InterviewQuestionsListResponse)
async def get_questions(
    learning_path_id: int,
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取面试题列表"""
    # 验证权限
    learning_path = db.query(LearningPath).filter(
        LearningPath.id == learning_path_id,
        LearningPath.user_id == current_user.id
    ).first()
    
    if not learning_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路线不存在"
        )
    
    # 构建查询
    query = db.query(InterviewQuestion).filter(
        InterviewQuestion.learning_path_id == learning_path_id
    )
    
    # 如果有状态筛选
    if status_filter and status_filter != "all":
        query = query.join(
            QuestionStatus,
            (QuestionStatus.question_id == InterviewQuestion.id) &
            (QuestionStatus.user_id == current_user.id)
        ).filter(QuestionStatus.status == status_filter)
    
    # 获取总数
    total = query.count()
    
    # 分页获取
    questions = query.order_by(InterviewQuestion.created_at.desc()).offset(offset).limit(limit).all()
    
    # 获取用户状态
    question_ids = [q.id for q in questions]
    statuses_dict = {}
    
    if question_ids:
        statuses = db.query(QuestionStatus).filter(
            QuestionStatus.user_id == current_user.id,
            QuestionStatus.question_id.in_(question_ids)
        ).all()
        
        statuses_dict = {
            s.question_id: {
                "status": s.status,
                "review_count": s.review_count,
                "last_reviewed_at": s.last_reviewed_at
            }
            for s in statuses
        }
    
    # 构建响应
    question_responses = []
    for q in questions:
        user_data = statuses_dict.get(q.id, {})
        question_responses.append(InterviewQuestionResponse(
            id=q.id,
            learning_path_id=q.learning_path_id,
            question=q.question,
            answer=q.answer,
            category=q.category,
            difficulty=q.difficulty,
            knowledge_points=q.knowledge_points,
            created_at=q.created_at,
            user_status=user_data.get("status", "not_seen"),
            review_count=user_data.get("review_count", 0),
            last_reviewed_at=user_data.get("last_reviewed_at")
        ))
    
    # 获取统计信息
    statistics_data = interview_service.get_statistics(
        db=db,
        user_id=current_user.id,
        learning_path_id=learning_path_id
    )
    
    statistics = InterviewStatistics(**statistics_data)
    
    return InterviewQuestionsListResponse(
        questions=question_responses,
        statistics=statistics,
        total=total,
        has_more=(offset + limit) < total
    )


@router.post("/status")
async def update_question_status(
    request: QuestionStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新题目状态"""
    # 验证题目存在
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == request.question_id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    # 验证用户权限
    learning_path = db.query(LearningPath).filter(
        LearningPath.id == question.learning_path_id,
        LearningPath.user_id == current_user.id
    ).first()
    
    if not learning_path:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问此题目"
        )
    
    # 查找或创建状态记录
    question_status = db.query(QuestionStatus).filter(
        QuestionStatus.user_id == current_user.id,
        QuestionStatus.question_id == request.question_id
    ).first()
    
    if question_status:
        # 更新现有记录
        question_status.status = request.status.value  # 转换为字符串
        question_status.review_count += 1
        question_status.last_reviewed_at = datetime.now()
        question_status.updated_at = datetime.now()
    else:
        # 创建新记录
        question_status = QuestionStatus(
            user_id=current_user.id,
            question_id=request.question_id,
            status=request.status.value,  # 转换为字符串
            review_count=1,
            last_reviewed_at=datetime.now()
        )
        db.add(question_status)
    
    db.commit()
    db.refresh(question_status)
    
    return {
        "success": True,
        "message": "状态更新成功",
        "status": question_status.status,
        "review_count": question_status.review_count
    }


@router.get("/statistics/{learning_path_id}", response_model=InterviewStatistics)
async def get_statistics(
    learning_path_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取刷题统计"""
    # 验证权限
    learning_path = db.query(LearningPath).filter(
        LearningPath.id == learning_path_id,
        LearningPath.user_id == current_user.id
    ).first()
    
    if not learning_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路线不存在"
        )
    
    statistics_data = interview_service.get_statistics(
        db=db,
        user_id=current_user.id,
        learning_path_id=learning_path_id
    )
    
    return InterviewStatistics(**statistics_data)


@router.post("/generate-weak-points", response_model=GenerateQuestionsResponse)
async def generate_weak_points_questions(
    learning_path_id: int,
    count: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """根据薄弱点生成针对性题目"""
    # 验证权限
    learning_path = db.query(LearningPath).filter(
        LearningPath.id == learning_path_id,
        LearningPath.user_id == current_user.id
    ).first()
    
    if not learning_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学习路线不存在"
        )
    
    # 分析薄弱点
    weak_analysis = interview_service.analyze_weak_points(
        db=db,
        user_id=current_user.id,
        learning_path_id=learning_path_id
    )
    
    if weak_analysis["not_mastered_count"] == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="暂无薄弱点数据，请先完成一些题目"
        )
    
    try:
        # 基于薄弱点生成题目
        questions = await interview_service.generate_questions(
            db=db,
            learning_path_id=learning_path_id,
            count=count,
            based_on_weak_points=True,
            weak_points=weak_analysis["weak_knowledge_points"]
        )
        
        # 转换为响应格式
        question_responses = []
        for q in questions:
            question_responses.append(InterviewQuestionResponse(
                id=q.id,
                learning_path_id=q.learning_path_id,
                question=q.question,
                answer=q.answer,
                category=q.category,
                difficulty=q.difficulty,
                knowledge_points=q.knowledge_points,
                created_at=q.created_at,
                user_status="not_seen",
                review_count=0
            ))
        
        return GenerateQuestionsResponse(
            success=True,
            message=f"基于薄弱点生成{len(questions)}道针对性题目",
            questions=question_responses,
            count=len(questions)
        )
        
    except Exception as e:
        print(f"[ERROR] 生成薄弱点题目失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成题目失败: {str(e)}"
        )

