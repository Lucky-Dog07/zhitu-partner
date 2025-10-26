from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionStatusEnum(str, Enum):
    NOT_SEEN = "not_seen"
    MASTERED = "mastered"
    NOT_MASTERED = "not_mastered"


# 请求模型
class InterviewQuestionGenerate(BaseModel):
    """生成面试题请求"""
    learning_path_id: int
    count: int = Field(default=20, ge=1, le=100)
    category: Optional[str] = None
    based_on_weak_points: bool = False


class QuestionStatusUpdate(BaseModel):
    """更新题目状态请求"""
    question_id: int
    status: QuestionStatusEnum


# 响应模型
class InterviewQuestionBase(BaseModel):
    """面试题基础模型"""
    question: str
    answer: str
    category: Optional[str] = None
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    knowledge_points: Optional[List[str]] = None


class InterviewQuestionCreate(InterviewQuestionBase):
    """创建面试题"""
    learning_path_id: int


class InterviewQuestionResponse(InterviewQuestionBase):
    """面试题响应（包含ID和状态）"""
    id: int
    learning_path_id: int
    created_at: datetime
    user_status: Optional[QuestionStatusEnum] = None  # 用户对该题的状态
    review_count: Optional[int] = 0
    last_reviewed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InterviewStatistics(BaseModel):
    """面试题统计"""
    total: int
    not_seen: int
    mastered: int
    not_mastered: int
    mastery_rate: float  # 掌握率
    weak_categories: List[dict]  # 薄弱分类 [{"category": "技术基础", "count": 5}]
    weak_knowledge_points: List[dict]  # 薄弱知识点 [{"point": "算法", "count": 3}]


class InterviewQuestionsListResponse(BaseModel):
    """面试题列表响应"""
    questions: List[InterviewQuestionResponse]
    statistics: InterviewStatistics
    total: int
    has_more: bool


class GenerateQuestionsResponse(BaseModel):
    """生成题目响应"""
    success: bool
    message: str
    questions: List[InterviewQuestionResponse]
    count: int

