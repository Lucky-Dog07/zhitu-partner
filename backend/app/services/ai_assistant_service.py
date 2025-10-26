"""
AI学习助手服务 - 基于LangChain的智能对话系统
"""
import os
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from sqlalchemy.orm import Session
from ..core.config_manager import config
from ..core.database import SessionLocal
from ..models.chat_history import ChatHistory
from .ai_assistant_tools import get_all_tools
import json

# Monkey patch修复langchain-openai的token usage bug（第三方API兼容性）
def _patched_create_usage_metadata(oai_token_usage: Dict[str, Any]) -> Dict[str, Any]:
    """修复后的usage metadata创建函数，处理None值"""
    input_tokens = oai_token_usage.get("prompt_tokens") or 0
    output_tokens = oai_token_usage.get("completion_tokens") or 0
    total_tokens = oai_token_usage.get("total_tokens") or (input_tokens + output_tokens)
    
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }

# 应用monkey patch
try:
    from langchain_openai.chat_models import base as openai_base
    openai_base._create_usage_metadata = _patched_create_usage_metadata
    print("[INFO] ✅ 已应用OpenAI API兼容性补丁")
except Exception as e:
    print(f"[WARNING] 无法应用API兼容性补丁: {e}")


class AIAssistantService:
    """AI学习助手服务类"""
    
    def __init__(self):
        # 从配置文件加载OpenAI配置
        openai_config = config.get_openai_config()
        
        # 检测是否为第三方API（需要特殊处理）
        base_url = openai_config.get('base_url', 'https://api.openai.com/v1')
        is_third_party = 'openai.com' not in base_url
        
        # 初始化OpenAI LLM
        # 注意：某些第三方API可能不完全兼容OpenAI的响应格式
        llm_kwargs = {
            'model': openai_config.get('model', 'gpt-4o-mini'),
            'api_key': openai_config.get('api_key'),
            'base_url': base_url,
            'temperature': openai_config.get('temperature', 0.3),
            'max_tokens': openai_config.get('max_tokens', 2000),
        }
        
        # 第三方API特殊配置
        if is_third_party:
            print(f"[INFO] 检测到第三方API: {base_url}，应用兼容性配置")
            llm_kwargs['streaming'] = False  # 禁用streaming
            llm_kwargs['request_timeout'] = 60  # 增加超时时间
        
        self.llm = ChatOpenAI(**llm_kwargs)
        
        # System Prompt (简化版，更好地支持中文)
        self.system_prompt = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do (in Chinese)
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (MUST be valid JSON, e.g. {{}}, {{"limit": 10}}, {{"category": "技术基础"}})
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer (in Chinese)
Final Answer: the final answer to the original input question (in Chinese)

IMPORTANT RULES:
1. Thought and Final Answer MUST be in Chinese (简体中文)
2. Action Input MUST be valid JSON format with double quotes, NOT Chinese text
3. For tools with no parameters, use empty dict: {{}}
4. Examples of valid Action Input:
   - {{}}
   - {{"limit": 10}}
   - {{"category": "技术基础", "limit": 5}}
5. Use Markdown format in Final Answer for better readability

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
        
        # 创建prompt template
        self.prompt = PromptTemplate(
            input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
            template=self.system_prompt
        )
    
    def create_agent(self, user_id: int) -> AgentExecutor:
        """为特定用户创建Agent"""
        # 为当前用户创建工具实例
        tools = get_all_tools(user_id)
        
        # 创建memory（保留最近10轮对话）
        memory = ConversationBufferWindowMemory(
            k=10,
            memory_key="chat_history",
            return_messages=True
        )
        
        # 从数据库加载历史对话（安全加载，确保所有字段都是字符串）
        try:
            history = self.get_conversation_history(user_id, limit=10)
            for msg in history:
                # 严格验证消息内容
                message_content = msg.get('message')
                message_role = msg.get('role')
                
                # 跳过无效消息
                if not message_content or message_content is None:
                    print(f"[WARNING] 跳过空消息: role={message_role}")
                    continue
                
                # 确保message是字符串类型
                if not isinstance(message_content, str):
                    print(f"[WARNING] 跳过非字符串消息: type={type(message_content)}")
                    continue
                
                # 确保message不是空字符串
                if message_content.strip() == "":
                    print(f"[WARNING] 跳过空白消息")
                    continue
                
                # 安全地添加到memory
                try:
                    if message_role == 'user':
                        memory.chat_memory.add_user_message(message_content)
                    elif message_role == 'assistant':
                        memory.chat_memory.add_ai_message(message_content)
                except Exception as mem_error:
                    print(f"[ERROR] 添加消息到Memory失败: {mem_error}")
                    continue
        except Exception as history_error:
            print(f"[ERROR] 加载历史对话失败: {history_error}")
            # 即使加载历史失败，也继续创建Agent（使用空memory）
        
        print(f"[DEBUG] 创建Agent，工具数量: {len(tools)}")
        for tool in tools:
            print(f"[DEBUG]   - {tool.name}: {tool.description[:50]}...")
        
        # 创建ReAct Agent
        agent = create_react_agent(
            llm=self.llm,
            tools=tools,
            prompt=self.prompt
        )
        
        # 创建Agent Executor（恢复memory，使用安全加载）
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            max_execution_time=120,
            return_intermediate_steps=False
        )
        
        return agent_executor
    
    def chat(self, user_id: int, message: str, db: Session) -> Dict[str, Any]:
        """
        处理用户消息
        
        Args:
            user_id: 用户ID
            message: 用户消息
            db: 数据库会话
            
        Returns:
            包含AI回复的字典
        """
        try:
            # 保存用户消息到数据库
            user_msg = ChatHistory(
                user_id=user_id,
                role="user",
                message=message
            )
            db.add(user_msg)
            db.commit()
            
            # 创建Agent（每次对话创建新的以确保状态隔离）
            agent_executor = self.create_agent(user_id)
            
            # 调用Agent（工具已绑定user_id，直接传递消息）
            print(f"[DEBUG] 开始调用Agent，用户消息: {message[:50]}...")
            try:
                response = agent_executor.invoke({
                    "input": message
                })
                print(f"[DEBUG] Agent响应: {response}")
            except Exception as agent_error:
                import traceback
                print(f"[ERROR] Agent执行错误: {agent_error}")
                print(f"[ERROR] Agent错误堆栈:\n{traceback.format_exc()}")
                raise  # 重新抛出，让外层catch处理
            
            ai_reply = response.get("output")
            
            # 确保ai_reply不为None
            if ai_reply is None or ai_reply == "":
                ai_reply = "抱歉，我现在无法理解您的问题。请换个方式再试试吧。"
                print(f"[WARNING] Agent返回了空值，使用默认回复")
            
            # 保存AI回复到数据库
            ai_msg = ChatHistory(
                user_id=user_id,
                role="assistant",
                message=ai_reply
            )
            db.add(ai_msg)
            db.commit()
            
            return {
                "success": True,
                "message": ai_reply
            }
            
        except Exception as e:
            import traceback
            print(f"[ERROR] AI助手聊天失败: {e}")
            print(f"[ERROR] 完整堆栈:\n{traceback.format_exc()}")
            # 即使失败也保存错误消息
            error_msg = "抱歉，我现在遇到了一些技术问题。请稍后再试，或者换个方式提问。"
            ai_msg = ChatHistory(
                user_id=user_id,
                role="assistant",
                message=error_msg
            )
            db.add(ai_msg)
            db.commit()
            
            return {
                "success": False,
                "message": error_msg,
                "error": str(e)
            }
    
    def get_conversation_history(
        self, 
        user_id: int, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取对话历史
        
        Args:
            user_id: 用户ID
            limit: 返回的消息数量
            
        Returns:
            对话历史列表
        """
        db = SessionLocal()
        try:
            messages = db.query(ChatHistory).filter(
                ChatHistory.user_id == user_id
            ).order_by(
                ChatHistory.created_at.asc()
            ).limit(limit).all()
            
            return [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "message": msg.message,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        finally:
            db.close()
    
    def clear_history(self, user_id: int, db: Session) -> bool:
        """
        清空用户对话历史
        
        Args:
            user_id: 用户ID
            db: 数据库会话
            
        Returns:
            是否成功
        """
        try:
            db.query(ChatHistory).filter(
                ChatHistory.user_id == user_id
            ).delete()
            db.commit()
            return True
        except Exception as e:
            print(f"[ERROR] 清空对话历史失败: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def get_quick_actions() -> List[Dict[str, str]]:
        """
        获取快捷功能列表
        
        Returns:
            快捷功能配置
        """
        return [
            {
                "id": "analyze_mistakes",
                "title": "分析我的错题",
                "description": "深度分析你的错题，找出薄弱环节",
                "prompt": "请帮我分析一下我的错题，找出我的薄弱知识点，并给出学习建议。",
                "icon": "BarChartOutlined"
            },
            {
                "id": "mock_interview",
                "title": "模拟面试",
                "description": "基于你的学习路线进行面试模拟",
                "prompt": "我想进行一次模拟面试，请随机选择一道面试题问我，我回答后请给出评价和改进建议。",
                "icon": "MessageOutlined"
            },
            {
                "id": "explain_concept",
                "title": "讲解知识点",
                "description": "深入浅出地讲解技术概念",
                "prompt": "我想学习一个技术知识点，请用通俗易懂的方式讲解，并配合代码示例。",
                "icon": "BulbOutlined"
            },
            {
                "id": "study_plan",
                "title": "学习计划建议",
                "description": "基于你的进度制定学习计划",
                "prompt": "请根据我的学习进度和错题情况，帮我制定一个详细的学习计划。",
                "icon": "CalendarOutlined"
            },
            {
                "id": "recommend_resources",
                "title": "推荐学习资源",
                "description": "推荐针对性的学习资源",
                "prompt": "请根据我的薄弱知识点，推荐一些优质的学习资源（书籍、课程、文档等）。",
                "icon": "BookOutlined"
            },
            {
                "id": "progress_report",
                "title": "学习进度报告",
                "description": "查看你的学习统计数据",
                "prompt": "请给我生成一份详细的学习进度报告，包括掌握率、错题分析等。",
                "icon": "DashboardOutlined"
            }
        ]


# 单例实例
ai_assistant_service = AIAssistantService()

