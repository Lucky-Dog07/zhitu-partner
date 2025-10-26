"""
AI 笔记生成服务
根据用户错题、面试题、学习路径等数据，生成个性化笔记
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Dict, List, Optional
import httpx
from ..core.config import settings
from ..models.learning_path import LearningPath
from ..models.interview_question import InterviewQuestion
from ..models.question_status import QuestionStatus
from ..prompts.note_templates import build_prompt


class AINoteGenerator:
    """AI 笔记生成器"""
    
    def __init__(self, db: Session):
        self.db = db
        
    async def generate_from_mistakes(
        self,
        user_id: int,
        learning_path_id: int,
        include_weak_points: bool = True,
        include_study_plan: bool = True,
        include_interview_tips: bool = True,
        custom_requirements: Optional[str] = None
    ) -> Dict:
        """
        基于错题生成笔记
        
        Args:
            user_id: 用户ID
            learning_path_id: 学习路径ID
            include_weak_points: 包含薄弱知识点分析
            include_study_plan: 包含学习计划
            include_interview_tips: 包含面试技巧
            custom_requirements: 自定义要求
            
        Returns:
            {title, content, suggested_notebook, metadata}
        """
        # 1. 获取学习路径信息
        learning_path = self.db.query(LearningPath).filter(
            LearningPath.id == learning_path_id,
            LearningPath.user_id == user_id
        ).first()
        
        if not learning_path:
            raise ValueError("学习路径不存在")
        
        position = learning_path.position
        
        # 2. 获取错题数据
        mistakes = self._get_user_mistakes(user_id, learning_path_id)
        
        # 3. 分析薄弱知识点
        weak_points = self._analyze_weak_points(user_id, learning_path_id) if include_weak_points else {}
        
        # 4. 构建学习进度描述
        learning_progress = self._build_learning_progress(user_id, learning_path_id)
        
        # 5. 构建 Prompt
        prompt = build_prompt(
            position=position,
            mistakes=mistakes,
            weak_points=weak_points,
            learning_progress=learning_progress,
            include_study_plan=include_study_plan,
            include_interview_tips=include_interview_tips,
            custom_requirements=custom_requirements
        )
        
        # 6. 调用 OpenAI 生成内容
        content = await self._call_openai_api(prompt)
        
        # 7. 返回结构化数据
        return {
            "title": f"{position} - 错题总结笔记",
            "content": content,
            "suggested_notebook": "错题本",
            "metadata": {
                "source": "mistakes",
                "learning_path_id": learning_path_id,
                "position": position,
                "mistakes_count": len(mistakes),
                "generated_at": datetime.now()
            }
        }
    
    async def generate_from_interview_questions(
        self,
        user_id: int,
        learning_path_id: int,
        include_weak_points: bool = True,
        include_study_plan: bool = True,
        include_interview_tips: bool = True,
        custom_requirements: Optional[str] = None
    ) -> Dict:
        """
        基于面试题生成笔记
        """
        # 获取学习路径信息
        learning_path = self.db.query(LearningPath).filter(
            LearningPath.id == learning_path_id,
            LearningPath.user_id == user_id
        ).first()
        
        if not learning_path:
            raise ValueError("学习路径不存在")
        
        position = learning_path.position
        
        # 获取所有面试题（限制前20题）
        interview_questions = self.db.query(InterviewQuestion).filter(
            InterviewQuestion.learning_path_id == learning_path_id
        ).limit(20).all()
        
        # 转换为列表格式
        questions_data = [
            {
                "question": q.question,
                "category": q.category,
                "difficulty": q.difficulty,
                "answer": q.answer
            }
            for q in interview_questions
        ]
        
        # 分析知识点分布
        weak_points = self._analyze_interview_weak_points(interview_questions) if include_weak_points else {}
        
        # 构建学习进度
        learning_progress = f"共 {len(interview_questions)} 道面试题"
        
        # 构建 Prompt（复用 mistakes 的逻辑，但调整内容）
        prompt = build_prompt(
            position=position,
            mistakes=questions_data,
            weak_points=weak_points,
            learning_progress=learning_progress,
            include_study_plan=include_study_plan,
            include_interview_tips=include_interview_tips,
            custom_requirements=custom_requirements
        )
        
        # 调用 OpenAI
        content = await self._call_openai_api(prompt)
        
        return {
            "title": f"{position} - 面试题总结笔记",
            "content": content,
            "suggested_notebook": "面试笔记",
            "metadata": {
                "source": "interview",
                "learning_path_id": learning_path_id,
                "position": position,
                "mistakes_count": len(questions_data),
                "generated_at": datetime.now()
            }
        }
    
    async def generate_from_learning_path(
        self,
        user_id: int,
        learning_path_id: int,
        include_weak_points: bool = True,
        include_study_plan: bool = True,
        include_interview_tips: bool = True,
        custom_requirements: Optional[str] = None
    ) -> Dict:
        """
        基于学习路径生成笔记
        """
        # 获取学习路径信息
        learning_path = self.db.query(LearningPath).filter(
            LearningPath.id == learning_path_id,
            LearningPath.user_id == user_id
        ).first()
        
        if not learning_path:
            raise ValueError("学习路径不存在")
        
        position = learning_path.position
        generated_content = learning_path.generated_content or {}
        
        # 提取学习路径的技能点和知识点
        skills = generated_content.get('skills', [])
        description = generated_content.get('description', '')
        
        # 构造学习路线数据
        learning_data = [
            {
                "question": f"技能点：{skill}",
                "reason": "需要掌握",
                "answer": "系统学习该技能点"
            }
            for skill in skills[:10]
        ]
        
        # 薄弱点分析
        weak_points = {"核心技能": skills[:5]} if include_weak_points else {}
        
        # 学习进度
        learning_progress = description
        
        # 构建 Prompt
        prompt = build_prompt(
            position=position,
            mistakes=learning_data,
            weak_points=weak_points,
            learning_progress=learning_progress,
            include_study_plan=include_study_plan,
            include_interview_tips=include_interview_tips,
            custom_requirements=custom_requirements
        )
        
        # 调用 OpenAI
        content = await self._call_openai_api(prompt)
        
        return {
            "title": f"{position} - 学习路径笔记",
            "content": content,
            "suggested_notebook": "学习笔记",
            "metadata": {
                "source": "learning_path",
                "learning_path_id": learning_path_id,
                "position": position,
                "mistakes_count": len(skills),
                "generated_at": datetime.now()
            }
        }
    
    def _get_user_mistakes(self, user_id: int, learning_path_id: int) -> List[Dict]:
        """获取用户错题"""
        # 查询状态为 not_mastered 的题目
        mistakes = self.db.query(
            InterviewQuestion, QuestionStatus
        ).join(
            QuestionStatus,
            (QuestionStatus.question_id == InterviewQuestion.id) &
            (QuestionStatus.user_id == user_id)
        ).filter(
            InterviewQuestion.learning_path_id == learning_path_id,
            QuestionStatus.status == 'not_mastered'
        ).limit(10).all()
        
        return [
            {
                "question": q.question,
                "category": q.category,
                "difficulty": q.difficulty,
                "reason": "未掌握",
                "answer": q.answer
            }
            for q, status in mistakes
        ]
    
    def _analyze_weak_points(self, user_id: int, learning_path_id: int) -> Dict[str, List[str]]:
        """分析薄弱知识点"""
        # 按分类统计错题
        weak_categories = self.db.query(
            InterviewQuestion.category,
            func.count(InterviewQuestion.id).label('count')
        ).join(
            QuestionStatus,
            (QuestionStatus.question_id == InterviewQuestion.id) &
            (QuestionStatus.user_id == user_id)
        ).filter(
            InterviewQuestion.learning_path_id == learning_path_id,
            QuestionStatus.status == 'not_mastered'
        ).group_by(
            InterviewQuestion.category
        ).order_by(
            func.count(InterviewQuestion.id).desc()
        ).limit(5).all()
        
        result = {}
        for category, count in weak_categories:
            # 获取该分类下的具体知识点
            questions = self.db.query(InterviewQuestion).join(
                QuestionStatus,
                (QuestionStatus.question_id == InterviewQuestion.id) &
                (QuestionStatus.user_id == user_id)
            ).filter(
                InterviewQuestion.learning_path_id == learning_path_id,
                InterviewQuestion.category == category,
                QuestionStatus.status == 'not_mastered'
            ).limit(3).all()
            
            # knowledge_points 是 JSON 字段，可能包含多个知识点
            knowledge_points_list = []
            for q in questions:
                if q.knowledge_points:
                    if isinstance(q.knowledge_points, list):
                        knowledge_points_list.extend(q.knowledge_points)
                    elif isinstance(q.knowledge_points, str):
                        knowledge_points_list.append(q.knowledge_points)
            result[category] = knowledge_points_list[:5]  # 最多5个
        
        return result
    
    def _analyze_interview_weak_points(self, questions: List[InterviewQuestion]) -> Dict[str, List[str]]:
        """分析面试题知识点分布"""
        result = {}
        for q in questions:
            category = q.category or "其他"
            if category not in result:
                result[category] = []
            
            # knowledge_points 是 JSON 字段，可能包含多个知识点
            if q.knowledge_points:
                if isinstance(q.knowledge_points, list):
                    for kp in q.knowledge_points:
                        if kp and kp not in result[category]:
                            result[category].append(kp)
                elif isinstance(q.knowledge_points, str):
                    if q.knowledge_points not in result[category]:
                        result[category].append(q.knowledge_points)
        return result
    
    def _build_learning_progress(self, user_id: int, learning_path_id: int) -> str:
        """构建学习进度描述"""
        # 统计总题数和掌握情况
        total = self.db.query(InterviewQuestion).filter(
            InterviewQuestion.learning_path_id == learning_path_id
        ).count()
        
        mastered = self.db.query(QuestionStatus).filter(
            QuestionStatus.user_id == user_id,
            QuestionStatus.status == 'mastered'
        ).join(InterviewQuestion).filter(
            InterviewQuestion.learning_path_id == learning_path_id
        ).count()
        
        not_mastered = self.db.query(QuestionStatus).filter(
            QuestionStatus.user_id == user_id,
            QuestionStatus.status == 'not_mastered'
        ).join(InterviewQuestion).filter(
            InterviewQuestion.learning_path_id == learning_path_id
        ).count()
        
        mastery_rate = round((mastered / total * 100) if total > 0 else 0, 1)
        
        return f"总题数：{total}，已掌握：{mastered}（{mastery_rate}%），未掌握：{not_mastered}"
    
    async def _call_openai_api(self, prompt: str) -> str:
        """调用 OpenAI API 生成内容"""
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{settings.OPENAI_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.OPENAI_MODEL,
                        "messages": [
                            {"role": "system", "content": "你是一位专业的学习顾问和笔记整理专家。"},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content']
            except Exception as e:
                raise Exception(f"OpenAI API 调用失败: {str(e)}")

