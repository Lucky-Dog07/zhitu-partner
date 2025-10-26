# 职途伴侣 - 多智能体协作架构说明

## 🤖 智能体系统概述

本项目采用**多智能体协作架构**，通过n8n工作流智能体和LangChain对话智能体的协同工作，实现智能化的职业技能提升服务。

## 🏗️ 智能体架构图

```
                        用户交互层
                            ↓
    ┌──────────────────────────────────────────┐
    │         FastAPI协调中心                    │
    │      (智能体任务分配与数据交换)              │
    └──────┬────────────────────────┬───────────┘
           ↓                        ↓
    ┌─────────────┐          ┌──────────────┐
    │ n8n工作流    │ ←─数据─→ │  LangChain   │
    │ 智能体系统   │   交换    │  智能体系统  │
    └─────────────┘          └──────────────┘
           ↓                        ↓
    ┌──────────────────────────────────────────┐
    │            共享知识库                      │
    │  (SQLite数据库 - 智能体间通信介质)         │
    └──────────────────────────────────────────┘
```

## 🔄 智能体协作场景

### 场景1：学习路线智能生成与分析

#### 智能体A：n8n工作流内容生成智能体

**位置**：`职途伴侣-核心工作流.json`

**职责**：
- 接收用户的职位描述（JD）
- 调用GPT-4分析技能要求
- 生成结构化学习内容

**输出数据**：
```json
{
  "learning_path_id": 123,
  "position": "AI工程师",
  "generated_content": {
    "mindmap": "# AI工程师技能树\n## 基础技能...",
    "knowledge_points": [...],
    "interview_questions": [...]
  }
}
```

**传递方式**：通过FastAPI保存到 `learning_paths` 表

#### 智能体B：LangChain对话分析智能体

**位置**：`backend/app/services/ai_assistant_service.py`

**职责**：
- 接收用户对话请求
- 调用Custom Tools访问智能体A生成的数据
- 基于数据提供个性化建议

**接收数据**：
```python
# GetLearningPathTool - 读取n8n智能体生成的学习路线
class GetLearningPathTool(BaseTool):
    def _run(self) -> str:
        # 从数据库读取n8n智能体生成的内容
        paths = db.query(LearningPath).filter(
            LearningPath.user_id == self.user_id
        ).all()
        
        # 分析内容并返回给LangChain Agent
        return f"用户的学习路线：{paths}..."
```

**协作流程**：
```
用户: "请根据我的学习路线给出建议"
    ↓
LangChain智能体: 调用GetLearningPathTool
    ↓
读取n8n智能体之前生成的学习路线数据
    ↓
LangChain智能体: 基于数据分析 + GPT推理
    ↓
输出: "根据您的AI工程师学习路线，建议先掌握Python基础..."
```

---

### 场景2：面试题生成与错题分析协作

#### 智能体A：n8n面试题生成智能体

**输入**：学习路线ID + 题目类型

**处理**：
1. 分析学习路线的知识点
2. 调用GPT生成针对性面试题
3. 将题目存储到 `interview_questions` 表

**输出示例**：
```json
{
  "question_id": 456,
  "question": "请解释Python中的GIL机制",
  "category": "Python基础",
  "difficulty": "medium",
  "answer": "详细答案...",
  "knowledge_points": ["GIL", "多线程", "并发"]
}
```

#### 智能体B：LangChain错题分析智能体

**Custom Tool**：`AnalyzeMistakesTool`

**职责**：
1. 读取用户的错题记录（`question_status` 表）
2. 分析错题的知识点分布
3. 识别薄弱环节
4. 生成针对性学习建议

**协作代码**：
```python
class AnalyzeMistakesTool(BaseTool):
    def _run(self) -> str:
        # 读取n8n生成的面试题 + 用户答题状态
        mistakes = db.query(QuestionStatus).filter(
            QuestionStatus.status == "not_mastered"
        ).join(InterviewQuestion).all()  # 关联n8n生成的题目
        
        # 统计薄弱知识点
        weak_points = {}
        for mistake in mistakes:
            for kp in mistake.question.knowledge_points:
                weak_points[kp] = weak_points.get(kp, 0) + 1
        
        # 返回分析结果给LangChain Agent
        return f"薄弱知识点：{weak_points}..."
```

**协作流程**：
```
用户刷题(n8n生成的题目) → 标记错题 → 存入数据库
                                      ↓
用户: "分析我的错题"
    ↓
LangChain智能体: 调用AnalyzeMistakesTool
    ↓
读取错题记录(关联n8n生成的题目数据)
    ↓
分析知识点分布 + GPT生成学习建议
    ↓
输出: "您在Python并发编程方面较薄弱，建议重点学习GIL机制..."
```

---

### 场景3：智能推荐系统的协作

#### 智能体A：n8n资源推荐智能体

**触发**：学习路线生成时

**处理**：
1. 分析目标职位的技能要求
2. 调用外部API搜索课程资源
3. 使用GPT筛选和排序资源
4. 存储推荐结果

**输出**：课程、书籍、证书推荐列表

#### 智能体B：LangChain个性化推荐智能体

**Custom Tool**：`GetRecommendationsTool`

**职责**：
1. 读取n8n生成的基础推荐
2. 结合用户学习进度
3. 结合错题分析结果
4. 生成个性化推荐

**协作流程**：
```
n8n智能体: 生成通用资源推荐(基于职位)
    ↓ 存入数据库
LangChain智能体: 读取推荐 + 用户数据
    ↓ 个性化筛选
    ↓
输出: "根据您的学习进度和薄弱点，建议先学习这门课程..."
```

---

### 场景4：模拟面试的多智能体协作

#### 智能体A：面试题库智能体（n8n）

**职责**：维护题库，生成面试题

#### 智能体B：面试官智能体（LangChain）

**位置**：`backend/app/services/interview_simulator.py`

**职责**：
- 模拟真实面试官
- 提问、追问、评估答案
- 生成面试报告

**协作代码**：
```python
class InterviewSimulator:
    def start_interview(self, learning_path_id: int):
        # 1. 从n8n生成的题库中选题
        questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.learning_path_id == learning_path_id
        ).all()
        
        # 2. LangChain Agent扮演面试官
        # 使用选中的题目进行对话式面试
        
    def evaluate_answer(self, answer: str):
        # 基于n8n生成的标准答案进行评估
        # 结合GPT生成详细反馈
```

**协作流程**：
```
n8n智能体: 生成面试题库
    ↓
用户: 开始模拟面试
    ↓
LangChain面试官智能体: 从题库选题
    ↓
实时对话、追问、评估
    ↓
生成面试报告(包含题目、答案、评分、建议)
```

---

## 🔗 智能体间的数据传递机制

### 1. 数据库作为共享知识库

```python
# n8n智能体 → 写入数据
POST /api/learning-paths
{
  "user_id": 1,
  "position": "AI工程师",
  "generated_content": {...}
}

# LangChain智能体 → 读取数据
class GetLearningPathTool(BaseTool):
    def _run(self):
        return db.query(LearningPath).filter(...)
```

### 2. Custom Tools作为通信桥梁

LangChain智能体通过6个Custom Tools访问n8n生成的数据：

1. **GetLearningPathTool** - 读取学习路线
2. **GetInterviewQuestionsTool** - 读取面试题
3. **GetMistakesTool** - 读取错题记录
4. **GetQuestionStatsTool** - 读取统计数据
5. **AnalyzeMistakesTool** - 分析错题分布
6. **GetRecommendationsTool** - 读取资源推荐

### 3. 异步协作模式

```
时刻T1: 用户请求 → n8n智能体生成内容(异步)
时刻T2: n8n完成 → 数据存入数据库
时刻T3: 用户对话 → LangChain智能体读取数据
时刻T4: LangChain基于数据 + 推理给出建议
```

---

## 🎯 多智能体协作的优势

### 1. 分工明确
- **n8n智能体**：擅长复杂工作流、内容生成、外部API调用
- **LangChain智能体**：擅长对话理解、推理分析、个性化建议

### 2. 数据复用
- n8n生成的内容可被多个LangChain智能体重复使用
- 避免重复调用LLM，节省成本

### 3. 解耦设计
- 智能体通过数据库松耦合
- 可独立升级、替换智能体

### 4. 异步处理
- n8n智能体可异步生成大量内容
- LangChain智能体实时响应用户对话

---

## 📊 智能体协作数据流图

```
┌─────────────────┐
│   用户请求      │
└────────┬────────┘
         ↓
┌────────────────────────────────┐
│     FastAPI路由层               │
│  判断任务类型，分配给对应智能体  │
└─────┬──────────────────┬───────┘
      ↓                  ↓
┌─────────────┐    ┌──────────────┐
│n8n工作流智能体│    │LangChain智能体│
│             │    │              │
│生成学习内容  │    │对话理解分析  │
│调用GPT生成   │    │调用Custom Tools│
│存储到数据库  │    │读取智能体A数据│
└─────┬───────┘    └───────┬──────┘
      ↓                    ↓
      └────────┬──────────┘
               ↓
    ┌──────────────────┐
    │   共享数据库      │
    │ learning_paths   │
    │interview_questions│
    │ question_status  │
    │   chat_history   │
    └──────────────────┘
```

---

## 🔧 技术实现细节

### n8n智能体核心节点
- **Webhook节点** - 接收任务
- **OpenAI Chat Model** - 内容生成
- **Function节点** - 数据处理
- **PostgreSQL/HTTP节点** - 数据存储

### LangChain智能体核心组件
- **ReAct Agent** - 推理与行动
- **Custom BaseTool** - 工具集
- **ConversationMemory** - 对话记忆
- **GPT-4** - 语言模型

---

## 💡 智能体协作的实际应用场景

### 场景：用户完整学习流程

1. **生成阶段**（n8n智能体主导）
   - 用户输入目标职位
   - n8n生成学习路线、面试题、资源推荐

2. **学习阶段**（LangChain智能体主导）
   - 用户："请帮我制定学习计划"
   - LangChain读取n8n生成的内容
   - 结合用户进度给出个性化计划

3. **练习阶段**（协作）
   - 用户刷n8n生成的面试题
   - 答题数据存入数据库
   - LangChain分析错题，给出建议

4. **复习阶段**（LangChain智能体）
   - LangChain识别薄弱知识点
   - 推荐n8n生成的相关学习内容
   - 生成复习计划

---

## 🚀 未来扩展方向

1. **增加更多智能体**
   - 代码审查智能体
   - 项目实战智能体
   - 职业规划智能体

2. **智能体协商机制**
   - Agent之间可以"讨论"最优方案
   - 多个Agent投票决策

3. **智能体学习能力**
   - 根据用户反馈优化推荐
   - Agent之间共享学习经验

---

**总结**：本项目通过n8n工作流智能体负责内容生成，LangChain对话智能体负责个性化分析，两者通过数据库进行数据传递和协作，实现了完整的多智能体协作系统。

