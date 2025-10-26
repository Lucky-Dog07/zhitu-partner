from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from ..core.config_manager import config
from ..models.interview_session import InterviewSession
from ..models.learning_path import LearningPath
from ..models.interview_question import InterviewQuestion
import random
import json
import datetime


class InterviewSimulator:
    """基于 LangChain 的面试模拟器"""
    
    def __init__(self, db: Session):
        self.db = db
        # 从配置文件加载OpenAI配置
        openai_config = config.get_openai_config()
        
        self.llm = ChatOpenAI(
            model=openai_config.get('model', 'gpt-4o-mini'),
            api_key=openai_config.get('api_key'),
            base_url=openai_config.get('base_url', 'https://api.openai.com/v1'),
            temperature=0.7  # 稍高温度使对话更自然
        )
    
    def _create_interviewer_prompt(self, position: str) -> str:
        """创建面试官 System Prompt"""
        return f"""你是一位经验丰富的{position}面试官。你的任务是：

1. 根据候选人回答质量，灵活决定是否追问或提出新问题
2. 追问策略：
   - 回答浅显 → 追问技术细节、实现原理
   - 回答模糊 → 要求举例说明、具体场景
   - 回答完整 → 认可后进入下一题
3. 保持专业友好的面试氛围
4. 每次回复100字以内，简洁有力

你可以：
- 深挖技术原理："你能详细说说这个技术的底层实现吗？"
- 实际应用："你在项目中是如何使用的？"
- 问题解决:"如果遇到XX问题，你会怎么处理？"
- 对比分析："为什么选择这个方案而不是其他方案？"

请根据对话历史，给出合适的追问或新问题。"""
    
    def start_session(self, user_id: int, learning_path_id: int) -> Dict[str, Any]:
        """开始新的面试会话"""
        # 获取学习路径
        path = self.db.query(LearningPath).filter(
            LearningPath.id == learning_path_id,
            LearningPath.user_id == user_id
        ).first()
        
        if not path:
            raise ValueError("学习路径不存在")
        
        # 随机选择开场题
        questions = self.db.query(InterviewQuestion).filter(
            InterviewQuestion.learning_path_id == learning_path_id
        ).all()
        
        if not questions:
            raise ValueError("该学习路径下没有面试题")
        
        first_q = random.choice(questions)
        
        # 创建会话
        system_prompt = self._create_interviewer_prompt(path.position)
        first_message = f"你好，欢迎参加{path.position}岗位的面试。让我们开始吧。\n\n{first_q.question}"
        
        session = InterviewSession(
            user_id=user_id,
            learning_path_id=learning_path_id,
            position=path.position,
            conversation=[
                {
                    "role": "system",
                    "content": system_prompt,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                },
                {
                    "role": "assistant",
                    "content": first_message,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }
            ]
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return {
            "session_id": session.id,
            "position": path.position,
            "first_message": first_message
        }
    
    def continue_conversation(
        self,
        session_id: int,
        user_id: int,
        answer: str
    ) -> Dict[str, Any]:
        """继续对话 - 使用 LangChain 生成追问"""
        session = self.db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id,
            InterviewSession.status == "in_progress"
        ).first()
        
        if not session:
            raise ValueError("会话不存在或已结束")
        
        # 添加用户回答
        session.conversation.append({
            "role": "user",
            "content": answer,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        
        # 使用 LangChain Memory 管理对话
        memory = ConversationBufferWindowMemory(k=10, return_messages=True)
        
        # 加载历史对话到 Memory
        for msg in session.conversation[1:]:  # 跳过 system
            if msg["role"] == "user":
                memory.chat_memory.add_user_message(msg["content"])
            elif msg["role"] == "assistant":
                memory.chat_memory.add_ai_message(msg["content"])
        
        # 构建 Prompt
        messages = [
            SystemMessage(content=session.conversation[0]["content"]),
            *memory.chat_memory.messages
        ]
        
        # 调用 LangChain
        response = self.llm.invoke(messages)
        interviewer_message = response.content
        
        # 保存面试官回复
        session.conversation.append({
            "role": "assistant",
            "content": interviewer_message,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        
        # 简单评估当前回答
        quality = self._quick_evaluate(answer, interviewer_message)
        
        self.db.commit()
        
        return {
            "interviewer_message": interviewer_message,
            "quality_hint": quality,
            "question_count": len([m for m in session.conversation if m["role"] == "user"])
        }
    
    def _quick_evaluate(self, answer: str, next_q: str) -> str:
        """快速评估回答质量"""
        if len(answer) < 30:
            return "needs_improvement"
        elif any(word in next_q for word in ["详细", "具体", "为什么", "如何"]):
            return "good"
        else:
            return "excellent"
    
    def end_session(self, session_id: int, user_id: int) -> Dict[str, Any]:
        """结束面试 - 使用 LangChain 生成评价报告"""
        session = self.db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id
        ).first()
        
        if not session:
            raise ValueError("会话不存在")
        
        # 计算时长
        duration = (datetime.datetime.utcnow() - session.started_at).seconds
        session.ended_at = datetime.datetime.utcnow()
        session.duration_seconds = duration
        session.status = "completed"
        
        # 使用 LangChain 生成评价
        evaluation = self._generate_evaluation_with_langchain(
            session.conversation,
            session.position
        )
        session.evaluation = evaluation
        
        self.db.commit()
        
        return {
            "session_id": session.id,
            "duration_minutes": duration // 60,
            "evaluation": evaluation
        }
    
    def _generate_evaluation_with_langchain(
        self,
        conversation: List[Dict],
        position: str
    ) -> Dict[str, Any]:
        """使用 LangChain 生成结构化评价报告"""
        # 格式化对话记录
        conv_text = []
        for msg in conversation[1:]:  # 跳过 system
            if msg["role"] == "user":
                conv_text.append(f"候选人：{msg['content']}")
            elif msg["role"] == "assistant":
                conv_text.append(f"面试官：{msg['content']}")
        
        conversation_str = "\n\n".join(conv_text)
        
        # 构建评价 Prompt
        evaluation_prompt = f"""你是{position}领域的资深面试官。请对以下面试表现进行全面评价。

面试对话记录：
{conversation_str}

请按照以下 JSON 格式输出评价（只返回 JSON，不要其他内容）：
{{
    "overall_score": 85,
    "dimension_scores": {{
        "technical_depth": 80,
        "expression": 85,
        "problem_solving": 90,
        "experience": 75
    }},
    "strengths": [
        "逻辑清晰，表达流畅",
        "对核心技术有深入理解"
    ],
    "weaknesses": [
        "实际项目经验不够具体",
        "部分原理理解有待加深"
    ],
    "suggestions": [
        "建议多做实际项目",
        "深入学习底层原理"
    ],
    "summary": "候选人基础扎实，表达清晰，建议加强实践经验..."
}}

评分标准（0-100）：
- technical_depth: 技术深度与原理理解
- expression: 表达能力与逻辑清晰度
- problem_solving: 问题解决思路
- experience: 实践经验与项目经历"""
        
        # 调用 LangChain 生成
        try:
            response = self.llm.invoke([
                SystemMessage(content="你是一位专业的面试评估专家，擅长客观评价候选人表现。"),
                HumanMessage(content=evaluation_prompt)
            ])
            
            # 解析 JSON
            evaluation = json.loads(response.content)
        except Exception as e:
            # 容错处理
            print(f"评价生成失败：{e}")
            evaluation = {
                "overall_score": 70,
                "dimension_scores": {
                    "technical_depth": 70,
                    "expression": 70,
                    "problem_solving": 70,
                    "experience": 70
                },
                "strengths": ["表达清晰"],
                "weaknesses": ["需要更多实践"],
                "suggestions": ["继续学习，多做项目"],
                "summary": "面试表现良好，继续努力。"
            }
        
        return evaluation

