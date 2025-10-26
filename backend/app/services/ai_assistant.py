from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Any
from ..core.config import settings


class AIAssistant:
    """LangChain智能助手"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_BASE_URL,
            temperature=0.7
        )
        
        self.system_prompt = """你是「职途伴侣」AI学习助手，专门帮助用户深入理解职业技能知识。

你的任务包括：
1. 深度讲解：为用户详细解释技能知识点，提供示例和最佳实践
2. 笔记整理：帮助用户整理学习笔记，形成结构化的知识体系
3. 面试评价：评价用户的面试回答，提供专业建议和改进方向
4. 学习建议：根据用户的学习进度，提供个性化的学习规划

请以专业、友好的态度回答，确保内容准确、实用。
"""
    
    async def chat(
        self,
        message: str,
        context: str = None,
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """
        与AI助手对话
        
        Args:
            message: 用户消息
            context: 可选的上下文信息
            chat_history: 对话历史
            
        Returns:
            AI的回复
        """
        messages = [SystemMessage(content=self.system_prompt)]
        
        # 添加上下文
        if context:
            messages.append(SystemMessage(content=f"相关内容：\n{context}"))
        
        # 添加历史对话（最近10条）
        if chat_history:
            for item in chat_history[-10:]:
                if item["role"] == "user":
                    messages.append(HumanMessage(content=item["message"]))
                elif item["role"] == "assistant":
                    messages.append(AIMessage(content=item["message"]))
        
        # 添加当前消息
        messages.append(HumanMessage(content=message))
        
        # 调用LLM
        response = await self.llm.ainvoke(messages)
        return response.content
    
    async def explain_knowledge(self, skill_name: str, knowledge_content: str) -> str:
        """深度讲解知识点"""
        prompt = f"""请深度讲解以下技能知识点：

技能：{skill_name}
内容：{knowledge_content}

请提供：
1. 详细的原理说明
2. 实际应用场景
3. 代码示例（如适用）
4. 学习建议和资源推荐
"""
        return await self.chat(prompt)
    
    async def organize_notes(self, notes: List[Dict[str, Any]]) -> str:
        """整理笔记"""
        notes_text = "\n\n".join([
            f"## {note.get('title', '无标题')}\n{note['content']}\n标签：{', '.join(note.get('tags', []))}"
            for note in notes
        ])
        
        prompt = f"""请帮我整理以下学习笔记，形成结构化的知识体系：

{notes_text}

请：
1. 按主题分类整理
2. 提取关键知识点
3. 建立知识点之间的关联
4. 标注重点和难点
5. 给出学习建议

以Markdown格式输出。
"""
        return await self.chat(prompt)
    
    async def evaluate_interview_answer(
        self,
        question: str,
        user_answer: str,
        reference_answer: str = None
    ) -> str:
        """评价面试回答"""
        prompt = f"""请评价以下面试回答：

面试题：{question}

用户回答：
{user_answer}
"""
        if reference_answer:
            prompt += f"\n参考答案：\n{reference_answer}"
        
        prompt += """

请从以下维度评价：
1. 准确性：回答是否准确
2. 完整性：是否覆盖关键点
3. 表达能力：逻辑是否清晰
4. 深度：是否展示深入理解
5. 改进建议：具体的优化方向

给出综合评分（1-10分）和详细的评价。
"""
        return await self.chat(prompt)


# 单例实例
ai_assistant = AIAssistant()

