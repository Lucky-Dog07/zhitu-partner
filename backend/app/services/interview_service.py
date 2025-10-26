import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import Counter
from openai import OpenAI
from ..models.interview_question import InterviewQuestion
from ..models.question_status import QuestionStatus
from ..models.learning_path import LearningPath
from ..core.config import settings


class InterviewService:
    """面试题生成和管理服务"""
    
    def __init__(self):
        """初始化OpenAI客户端"""
        self.openai_client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
    
    async def generate_questions(
        self,
        db: Session,
        learning_path_id: int,
        count: int = 20,
        category: Optional[str] = None,
        based_on_weak_points: bool = False,
        weak_points: Optional[List[str]] = None
    ) -> List[InterviewQuestion]:
        """
        生成面试题
        
        Args:
            db: 数据库session
            learning_path_id: 学习路线ID
            count: 生成数量
            category: 题目类型
            based_on_weak_points: 是否基于薄弱点生成
            weak_points: 薄弱知识点列表
        """
        # 获取学习路线信息
        learning_path = db.query(LearningPath).filter(
            LearningPath.id == learning_path_id
        ).first()
        
        if not learning_path:
            raise ValueError("学习路线不存在")
        
        # 构建生成提示词
        if based_on_weak_points and weak_points:
            prompt = self._build_weak_points_prompt(
                learning_path.position,
                weak_points,
                count
            )
        else:
            prompt = self._build_normal_prompt(
                learning_path.position,
                category,
                count
            )
        
        print(f"[DEBUG] 开始调用OpenAI生成面试题")
        print(f"[DEBUG] 职位: {learning_path.position}")
        print(f"[DEBUG] 题目数量: {count}")
        
        # 直接调用OpenAI API生成题目
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的面试题生成专家。你必须严格按照要求返回纯JSON格式的面试题，不要添加任何其他文字或markdown格式。每道题的答案要简洁明了，控制在150字以内。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=10000  # 增加到10000以确保20道题能完整返回
            )
            
            ai_output = response.choices[0].message.content
            print(f"[DEBUG] OpenAI返回内容长度: {len(ai_output)}")
            print(f"[DEBUG] OpenAI返回内容预览: {ai_output[:300]}")
            
            # 解析AI返回的题目
            questions_data = self._parse_ai_response({"output": ai_output})
            
        except Exception as e:
            print(f"[ERROR] ❌ OpenAI调用失败: {type(e).__name__}: {e}")
            raise Exception(f"面试题生成失败: {str(e)}")
        
        # 保存到数据库
        saved_questions = []
        for q_data in questions_data[:count]:  # 限制数量
            # 规范化difficulty值（转为小写）
            raw_difficulty = q_data.get("difficulty", "medium")
            normalized_difficulty = raw_difficulty.lower() if isinstance(raw_difficulty, str) else "medium"
            
            # 验证difficulty值是否有效
            if normalized_difficulty not in ['easy', 'medium', 'hard']:
                print(f"[WARN] 无效的difficulty值: {raw_difficulty}，使用默认值medium")
                normalized_difficulty = "medium"
            
            print(f"[DEBUG] difficulty转换: {raw_difficulty} -> {normalized_difficulty}")
            
            question = InterviewQuestion(
                learning_path_id=learning_path_id,
                question=q_data.get("question", ""),
                answer=q_data.get("answer", ""),
                category=q_data.get("category"),
                difficulty=normalized_difficulty,  # 直接使用字符串
                knowledge_points=q_data.get("knowledge_points", [])
            )
            db.add(question)
            saved_questions.append(question)
        
        print(f"[DEBUG] 准备提交 {len(saved_questions)} 道题目到数据库")
        
        db.commit()
        for q in saved_questions:
            db.refresh(q)
        
        return saved_questions
    
    def _build_normal_prompt(self, position: str, category: Optional[str], count: int) -> str:
        """构建普通生成提示词"""
        prompt = f"""请为"{position}"职位生成{count}道面试题。

要求：
1. **必须**返回纯JSON格式，不要markdown代码块，不要其他文字说明
2. 题目要专业、实用、有针对性
3. 涵盖技术基础、项目经验、行为面试等多种类型
4. 每题包含详细的参考答案
5. 标注题目类别和难度
6. 提取关键知识点

"""
        
        if category:
            prompt += f"7. 重点生成【{category}】类型的题目\n\n"
        
        prompt += """
**直接返回以下JSON格式（不要用```json包裹，不要其他文字）：**

{{
  "questions": [
    {{
      "question": "题目内容",
      "answer": "详细的参考答案",
      "category": "技术基础/项目经验/行为面试/算法设计/系统架构等",
      "difficulty": "easy/medium/hard",
      "knowledge_points": ["知识点1", "知识点2"]
    }}
  ]
}}
"""
        return prompt
    
    def _build_weak_points_prompt(self, position: str, weak_points: List[str], count: int) -> str:
        """构建基于薄弱点的生成提示词"""
        weak_points_str = "、".join(weak_points[:5])  # 最多5个
        
        prompt = f"""请为"{position}"职位生成{count}道面试题。

用户在以下知识点上较为薄弱，请针对性出题：
{weak_points_str}

要求：
1. **必须**返回纯JSON格式，不要markdown代码块，不要其他文字说明
2. 题目重点考察上述薄弱知识点
3. 从基础到进阶，循序渐进
4. 每题包含详细解答和知识点分析
5. 帮助用户巩固薄弱环节

**直接返回以下JSON格式（不要用```json包裹，不要其他文字）：**

{{{{
  "questions": [
    {{{{
      "question": "题目内容",
      "answer": "详细的参考答案",
      "category": "题目类型",
      "difficulty": "easy/medium/hard",
      "knowledge_points": ["知识点1", "知识点2"]
    }}}}
  ]
}}}}
"""
        return prompt
    
    def _parse_ai_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析AI返回的题目数据"""
        output = data.get("output", "")
        
        print(f"[DEBUG] 开始解析AI返回数据")
        print(f"[DEBUG] data keys: {list(data.keys())}")
        print(f"[DEBUG] output type: {type(output)}")
        print(f"[DEBUG] output preview: {str(output)[:200]}")
        
        # 如果output为空，尝试直接从data中获取
        if not output:
            # 可能AI直接返回在data根节点
            if "questions" in data:
                print(f"[DEBUG] 在data根节点找到questions")
                return data["questions"]
            # 或者在data的其他字段
            for key in data:
                value = data[key]
                if isinstance(value, dict) and "questions" in value:
                    print(f"[DEBUG] 在data.{key}找到questions")
                    return value["questions"]
        
        # 尝试从output中提取JSON
        try:
            # 方法1: output直接是JSON字符串
            if isinstance(output, str) and output.strip().startswith("{"):
                print(f"[DEBUG] 尝试直接解析JSON")
                parsed = json.loads(output)
                if "questions" in parsed:
                    print(f"[DEBUG] ✅ 成功解析，找到{len(parsed['questions'])}道题")
                    return parsed["questions"]
            
            # 方法2: 从markdown代码块中提取
            if isinstance(output, str) and "```json" in output:
                print(f"[DEBUG] 尝试从```json代码块提取")
                start = output.find("```json") + 7
                end = output.find("```", start)
                json_str = output[start:end].strip()
                parsed = json.loads(json_str)
                if "questions" in parsed:
                    print(f"[DEBUG] ✅ 成功从代码块解析，找到{len(parsed['questions'])}道题")
                    return parsed["questions"]
            
            # 方法3: 查找第一个完整的JSON对象
            if isinstance(output, str):
                print(f"[DEBUG] 尝试查找JSON对象")
                start = output.find("{")
                end = output.rfind("}") + 1
                if start != -1 and end > start:
                    json_str = output[start:end]
                    print(f"[DEBUG] 提取的JSON字符串: {json_str[:100]}...")
                    parsed = json.loads(json_str)
                    if "questions" in parsed:
                        print(f"[DEBUG] ✅ 成功查找并解析，找到{len(parsed['questions'])}道题")
                        return parsed["questions"]
            
            # 方法4: output可能已经是dict
            if isinstance(output, dict):
                print(f"[DEBUG] output已经是dict")
                if "questions" in output:
                    print(f"[DEBUG] ✅ dict中找到questions，共{len(output['questions'])}道题")
                    return output["questions"]
                
        except json.JSONDecodeError as e:
            print(f"[ERROR] ❌ 解析AI返回的JSON失败: {e}")
            print(f"[ERROR] 原始输出前500字符: {str(output)[:500]}")
        except Exception as e:
            print(f"[ERROR] ❌ 解析过程出错: {type(e).__name__}: {e}")
        
        print(f"[ERROR] ❌ 所有解析方法失败，返回空列表")
        return []
    
    def analyze_weak_points(
        self,
        db: Session,
        user_id: int,
        learning_path_id: int
    ) -> Dict[str, Any]:
        """
        分析用户薄弱点
        
        返回：
        {
            "weak_knowledge_points": ["知识点1", "知识点2"],
            "weak_categories": ["类别1", "类别2"],
            "not_mastered_count": 10
        }
        """
        # 查询所有未掌握的题目
        not_mastered_questions = db.query(InterviewQuestion).join(
            QuestionStatus,
            (QuestionStatus.question_id == InterviewQuestion.id) &
            (QuestionStatus.user_id == user_id) &
            (QuestionStatus.status == "not_mastered")
        ).filter(
            InterviewQuestion.learning_path_id == learning_path_id
        ).all()
        
        # 统计薄弱知识点
        all_knowledge_points = []
        all_categories = []
        
        for q in not_mastered_questions:
            if q.knowledge_points:
                all_knowledge_points.extend(q.knowledge_points)
            if q.category:
                all_categories.append(q.category)
        
        # 统计频率
        knowledge_counter = Counter(all_knowledge_points)
        category_counter = Counter(all_categories)
        
        return {
            "weak_knowledge_points": [k for k, _ in knowledge_counter.most_common(10)],
            "weak_categories": [c for c, _ in category_counter.most_common(5)],
            "not_mastered_count": len(not_mastered_questions)
        }
    
    def get_statistics(
        self,
        db: Session,
        user_id: int,
        learning_path_id: int
    ) -> Dict[str, Any]:
        """获取刷题统计"""
        # 获取所有题目
        questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.learning_path_id == learning_path_id
        ).all()
        
        total = len(questions)
        if total == 0:
            return {
                "total": 0,
                "not_seen": 0,
                "mastered": 0,
                "not_mastered": 0,
                "mastery_rate": 0.0,
                "weak_categories": [],
                "weak_knowledge_points": []
            }
        
        # 统计各状态数量
        status_counts = db.query(
            QuestionStatus.status,
            func.count(QuestionStatus.id)
        ).join(
            InterviewQuestion,
            QuestionStatus.question_id == InterviewQuestion.id
        ).filter(
            QuestionStatus.user_id == user_id,
            InterviewQuestion.learning_path_id == learning_path_id
        ).group_by(QuestionStatus.status).all()
        
        status_dict = {status: count for status, count in status_counts}
        
        mastered = status_dict.get("mastered", 0)
        not_mastered = status_dict.get("not_mastered", 0)
        seen = mastered + not_mastered
        not_seen = total - seen
        
        # 计算掌握率
        mastery_rate = (mastered / seen * 100) if seen > 0 else 0.0
        
        # 分析薄弱点
        weak_analysis = self.analyze_weak_points(db, user_id, learning_path_id)
        
        # 统计薄弱类别
        weak_categories = []
        if weak_analysis["weak_categories"]:
            for category in weak_analysis["weak_categories"]:
                count = db.query(func.count(InterviewQuestion.id)).join(
                    QuestionStatus,
                    (QuestionStatus.question_id == InterviewQuestion.id) &
                    (QuestionStatus.user_id == user_id) &
                    (QuestionStatus.status == "not_mastered")
                ).filter(
                    InterviewQuestion.learning_path_id == learning_path_id,
                    InterviewQuestion.category == category
                ).scalar()
                
                weak_categories.append({"category": category, "count": count})
        
        # 统计薄弱知识点
        weak_knowledge_points = []
        if weak_analysis["weak_knowledge_points"]:
            for point in weak_analysis["weak_knowledge_points"][:10]:
                weak_knowledge_points.append({"point": point, "count": 0})  # 简化处理
        
        return {
            "total": total,
            "not_seen": not_seen,
            "mastered": mastered,
            "not_mastered": not_mastered,
            "mastery_rate": round(mastery_rate, 1),
            "weak_categories": weak_categories,
            "weak_knowledge_points": weak_knowledge_points
        }


interview_service = InterviewService()

