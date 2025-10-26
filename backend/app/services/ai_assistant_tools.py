"""
AI助手的Custom Tools - 用于访问用户学习数据
"""
from langchain.tools import BaseTool
from typing import Type, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..models.question_status import QuestionStatus
from ..models.interview_question import InterviewQuestion
from ..models.learning_path import LearningPath
from ..core.database import SessionLocal


# Tool Input Schemas (simplified - no user_id needed)
class GetMistakesInput(BaseModel):
    """错题查询输入 - 允许空参数"""
    pass  # No required input


class GetLearningPathInput(BaseModel):
    pass  # No input needed


class GetQuestionStatsInput(BaseModel):
    pass  # No input needed


class AnalyzeMistakesInput(BaseModel):
    pass  # No input needed


class GetInterviewQuestionsInput(BaseModel):
    """面试题查询输入 - 允许空参数"""
    pass  # No required input


# Custom Tools
class GetMistakesTool(BaseTool):
    """获取用户错题的工具"""
    name: str = "get_mistakes"
    description: str = "获取用户的错题列表，包括题目、答案和知识点。用于分析用户的薄弱环节。"
    args_schema: Type[BaseModel] = GetMistakesInput
    user_id: int = Field(default=0, description="当前用户ID")
    
    def _run(self) -> str:
        """查询用户错题"""
        db = SessionLocal()
        try:
            # 查询用户的错题（默认10条）
            mistakes = db.query(QuestionStatus).filter(
                QuestionStatus.user_id == self.user_id,
                QuestionStatus.status == "not_mastered"
            ).join(InterviewQuestion).limit(10).all()
            
            if not mistakes:
                return "用户目前没有错题记录。"
            
            result = f"找到 {len(mistakes)} 道错题：\n\n"
            for i, mistake in enumerate(mistakes, 1):
                q = mistake.question
                result += f"{i}. **题目**: {q.question[:100]}...\n"
                result += f"   **分类**: {q.category or '未分类'}\n"
                result += f"   **难度**: {q.difficulty}\n"
                result += f"   **知识点**: {', '.join(q.knowledge_points) if q.knowledge_points else '无'}\n"
                result += f"   **答案**: {q.answer[:150]}...\n\n"
            
            return result
        finally:
            db.close()


class GetLearningPathTool(BaseTool):
    """获取用户学习路线的工具"""
    name: str = "get_learning_path"
    description: str = "获取用户的学习路线和目标职位信息。用于了解用户的学习方向和已生成的学习内容。"
    args_schema: Type[BaseModel] = GetLearningPathInput
    user_id: int = Field(default=0, description="当前用户ID")
    
    def _run(self) -> str:
        """查询用户学习路线"""
        db = SessionLocal()
        try:
            paths = db.query(LearningPath).filter(
                LearningPath.user_id == self.user_id
            ).order_by(LearningPath.created_at.desc()).limit(3).all()
            
            if not paths:
                return "用户还没有创建学习路线。"
            
            result = f"用户的学习路线（最近{len(paths)}个）：\n\n"
            for i, path in enumerate(paths, 1):
                result += f"{i}. **目标职位**: {path.position}\n"
                if path.job_description:
                    result += f"   **职位描述**: {path.job_description[:100]}...\n"
                
                # 分析已生成的内容
                if path.generated_content:
                    content_types = []
                    if path.generated_content.get('mindmap'):
                        content_types.append('思维导图')
                    if path.generated_content.get('knowledge'):
                        content_types.append('知识点详解')
                    if path.generated_content.get('interview'):
                        content_types.append('面试题库')
                    if content_types:
                        result += f"   **已生成内容**: {', '.join(content_types)}\n"
                
                result += f"   **创建时间**: {path.created_at.strftime('%Y-%m-%d')}\n\n"
            
            return result
        finally:
            db.close()


class GetQuestionStatsTool(BaseTool):
    """获取用户学习统计数据的工具"""
    name: str = "get_question_stats"
    description: str = "获取用户的学习统计数据，包括已掌握、未掌握、总题数等。用于评估学习进度。"
    args_schema: Type[BaseModel] = GetQuestionStatsInput
    user_id: int = Field(default=0, description="当前用户ID")
    
    def _run(self) -> str:
        """统计用户学习数据"""
        db = SessionLocal()
        try:
            # 统计各状态的题目数量
            total = db.query(QuestionStatus).filter(
                QuestionStatus.user_id == self.user_id
            ).count()
            
            mastered = db.query(QuestionStatus).filter(
                QuestionStatus.user_id == self.user_id,
                QuestionStatus.status == "mastered"
            ).count()
            
            not_mastered = db.query(QuestionStatus).filter(
                QuestionStatus.user_id == self.user_id,
                QuestionStatus.status == "not_mastered"
            ).count()
            
            not_seen = total - mastered - not_mastered
            
            if total == 0:
                return "用户还没有开始练习题目。"
            
            mastery_rate = (mastered / total * 100) if total > 0 else 0
            
            result = f"📊 **学习统计数据**：\n\n"
            result += f"- 总题数: {total}\n"
            result += f"- 已掌握: {mastered} ({mastered/total*100:.1f}%)\n"
            result += f"- 未掌握: {not_mastered} ({not_mastered/total*100:.1f}%)\n"
            result += f"- 未练习: {not_seen} ({not_seen/total*100:.1f}%)\n"
            result += f"- 掌握率: {mastery_rate:.1f}%\n\n"
            
            if mastery_rate >= 80:
                result += "✅ 学习进度优秀！继续保持！"
            elif mastery_rate >= 60:
                result += "👍 学习进度良好，继续努力！"
            elif mastery_rate >= 40:
                result += "💪 还需要加油，建议重点复习错题。"
            else:
                result += "⚠️ 需要加强学习，建议系统复习知识点。"
            
            return result
        finally:
            db.close()


class AnalyzeMistakesTool(BaseTool):
    """分析用户错题知识点分布的工具"""
    name: str = "analyze_mistakes"
    description: str = "深度分析用户错题的知识点分布，找出薄弱环节。返回Top薄弱知识点和建议。"
    args_schema: Type[BaseModel] = AnalyzeMistakesInput
    user_id: int = Field(default=0, description="当前用户ID")
    
    def _run(self) -> str:
        """分析错题知识点分布"""
        db = SessionLocal()
        try:
            # 获取所有错题
            mistakes = db.query(QuestionStatus).filter(
                QuestionStatus.user_id == self.user_id,
                QuestionStatus.status == "not_mastered"
            ).join(InterviewQuestion).all()
            
            if not mistakes:
                return "用户目前没有错题，无需分析。"
            
            # 统计知识点分布
            knowledge_points_count = {}
            category_count = {}
            difficulty_count = {}
            
            for mistake in mistakes:
                q = mistake.question
                
                # 统计知识点
                if q.knowledge_points:
                    for kp in q.knowledge_points:
                        knowledge_points_count[kp] = knowledge_points_count.get(kp, 0) + 1
                
                # 统计分类
                category = q.category or "未分类"
                category_count[category] = category_count.get(category, 0) + 1
                
                # 统计难度
                difficulty_count[q.difficulty] = difficulty_count.get(q.difficulty, 0) + 1
            
            # 生成分析报告
            result = f"🔍 **错题深度分析报告**\n\n"
            result += f"总错题数: {len(mistakes)}\n\n"
            
            # Top薄弱知识点
            if knowledge_points_count:
                result += "### 📌 薄弱知识点 Top 5\n\n"
                sorted_kp = sorted(knowledge_points_count.items(), key=lambda x: x[1], reverse=True)[:5]
                for i, (kp, count) in enumerate(sorted_kp, 1):
                    percentage = count / len(mistakes) * 100
                    result += f"{i}. **{kp}**: {count}道错题 ({percentage:.1f}%)\n"
                result += "\n"
            
            # 错题分类分布
            if category_count:
                result += "### 📂 错题分类分布\n\n"
                for category, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / len(mistakes) * 100
                    result += f"- {category}: {count}道 ({percentage:.1f}%)\n"
                result += "\n"
            
            # 难度分布
            if difficulty_count:
                result += "### 📊 错题难度分布\n\n"
                for difficulty, count in sorted(difficulty_count.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / len(mistakes) * 100
                    result += f"- {difficulty}: {count}道 ({percentage:.1f}%)\n"
                result += "\n"
            
            # 学习建议
            result += "### 💡 学习建议\n\n"
            if knowledge_points_count:
                top_weak = sorted_kp[0][0]
                result += f"1. 重点复习「{top_weak}」相关知识点\n"
                result += f"2. 建议针对薄弱点做专项练习\n"
                result += f"3. 可以询问我详细讲解任何知识点\n"
            
            return result
        finally:
            db.close()


class GetInterviewQuestionsTool(BaseTool):
    """获取面试题的工具"""
    name: str = "get_interview_questions"
    description: str = "获取用户学习路线中的面试题，可按分类筛选。用于模拟面试或练习。"
    args_schema: Type[BaseModel] = GetInterviewQuestionsInput
    user_id: int = Field(default=0, description="当前用户ID")
    
    def _run(self) -> str:
        """获取面试题"""
        db = SessionLocal()
        try:
            # 先获取用户的学习路线
            paths = db.query(LearningPath).filter(
                LearningPath.user_id == self.user_id
            ).all()
            
            if not paths:
                return "用户还没有创建学习路线，无法获取面试题。"
            
            path_ids = [p.id for p in paths]
            
            # 查询面试题（默认5条）
            questions = db.query(InterviewQuestion).filter(
                InterviewQuestion.learning_path_id.in_(path_ids)
            ).limit(5).all()
            
            if not questions:
                return "没有找到面试题。建议先生成学习路线并添加面试题。"
            
            result = f"找到 {len(questions)} 道面试题：\n\n"
            for i, q in enumerate(questions, 1):
                result += f"{i}. **题目**: {q.question}\n"
                result += f"   **分类**: {q.category or '未分类'}\n"
                result += f"   **难度**: {q.difficulty}\n"
                result += f"   **参考答案**: {q.answer[:200]}...\n\n"
            
            return result
        finally:
            db.close()


# 导出所有工具
def get_all_tools(user_id: int) -> List[BaseTool]:
    """
    获取所有AI助手工具（为特定用户创建）
    
    Args:
        user_id: 用户ID，用于绑定到每个工具实例
        
    Returns:
        工具列表
    """
    return [
        GetMistakesTool(user_id=user_id),
        GetLearningPathTool(user_id=user_id),
        GetQuestionStatsTool(user_id=user_id),
        AnalyzeMistakesTool(user_id=user_id),
        GetInterviewQuestionsTool(user_id=user_id),
    ]

