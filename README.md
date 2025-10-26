# 职途伴侣 - AI驱动的职业技能提升平台

> 基于 FastAPI + React + n8n + LangChain 的智能职业规划与学习辅助系统

## 📚 项目简介

职途伴侣是一个全栈AI应用，通过整合大语言模型、工作流自动化和现代Web技术，为用户提供个性化的职业技能提升方案。

### ✨ 核心功能

- 🎯 **智能学习路线生成** - 基于职位JD自动生成个性化技能学习路径
- 🗺️ **可视化思维导图** - 以思维导图形式展示技能知识体系
- 📖 **AI知识点详解** - 三层次（专业/通俗/实例）知识解析
- 💬 **智能学习助手** - 基于LangChain Agent的对话式AI导师
- 📝 **智能笔记系统** - Markdown + 富文本双模式笔记，支持AI生成
- 💼 **模拟面试训练** - AI面试官实时对话，评估反馈
- 📚 **动态资源推荐** - 实时搜索B站、慕课网等平台课程资源
- 📊 **学习进度追踪** - 可视化展示学习统计和薄弱知识点
- 👔 **管理后台系统** - 用户管理、数据分析、系统配置一站式管理

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端层 (React + Vite)                  │
│  TypeScript + Ant Design + Zustand + React Router        │
└───────────────────┬─────────────────────────────────────┘
                    │ HTTP/WebSocket
┌───────────────────▼─────────────────────────────────────┐
│                 后端API层 (FastAPI)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │用户管理   │ │学习路线  │ │笔记系统  │ │数据统计  │  │
│  │认证鉴权   │ │面试题库  │ │AI助手    │ │管理后台  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└───────────────────┬─────────────────────────────────────┘
                    │
         ┌──────────┼──────────┐
         │                     │
┌────────▼────────┐   ┌───────▼────────┐
│  n8n工作流引擎   │   │ LangChain Agent │
│  (学习内容生成)   │   │  (AI对话助手)    │
└────────┬────────┘   └───────┬────────┘
         │                     │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │    OpenAI API / LLM  │
         └─────────────────────┘
                    │
         ┌──────────▼──────────┐
         │  SQLite / PostgreSQL │
         │   (用户数据 + 学习记录) │
         └─────────────────────┘
```

## 🚀 快速开始

### 前置要求

- **Python 3.9+**
- **Node.js 18+** 
- **n8n** (通过Docker运行)
- **OpenAI API Key** (或兼容的第三方API)

### 1. 克隆项目

```bash
git clone [项目地址]
cd 职途伴侣
```

### 2. 后端配置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置API密钥
cp config.example.json config.json
# 编辑 config.json，填入您的OpenAI API Key和n8n Webhook URL

# 初始化数据库
python init_db.py

# (可选) 创建管理员账号
python create_admin.py

# 启动后端服务
python -m uvicorn app.main:app --reload --port 8000
```

**配置说明：**
```json
{
  "openai": {
    "api_key": "your-api-key",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4o-mini"
  },
  "n8n": {
    "webhook_url": "http://localhost:5678/webhook/zhitu-learning"
  }
}
```

详细配置请参考：`backend/README.md`

### 3. 前端配置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 启动

### 4. n8n工作流配置

```bash
# 启动n8n (使用Docker)
docker run -d \
  -p 5678:5678 \
  --name n8n \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# 访问 http://localhost:5678
# 导入工作流文件：
# - 职途伴侣-核心工作流.json
# - 职途伴侣-学习交互工作流.json
```

### 5. 一键启动（推荐）

```bash
# 项目根目录执行
./start-all.sh
```

自动启动：
- ✅ n8n工作流引擎
- ✅ 后端API服务
- ✅ 前端开发服务器

## 📖 功能说明

### 1. 学习路线生成

基于职位描述，AI自动分析技能要求并生成：
- 🗺️ 技能思维导图
- 📚 知识点详细解析
- 💼 模拟面试题库
- 📖 课程资源推荐

### 2. AI学习助手

基于LangChain Agent的智能助手，可以：
- 分析错题，找出薄弱知识点
- 制定个性化学习计划
- 推荐学习资源
- 解答技术问题
- 追踪学习进度

### 3. 智能笔记系统

- 📝 双模式编辑器（Markdown + 富文本）
- 🗂️ 笔记本分类管理
- 🧠 思维导图视图
- 🤖 AI笔记生成
- 🔗 一键从面试题、学习路线生成笔记

### 4. 模拟面试

- 💼 实时AI面试官对话
- 📊 多维度评估反馈
- 📈 面试历史记录
- 🎯 针对性提升建议

### 5. 管理后台

- 👥 用户管理
- 📊 数据统计分析
- 📈 可视化仪表板
- 📝 操作日志审计
- ⚙️ 系统配置管理

## 🔧 项目结构

```
职途伴侣/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API路由
│   │   │   ├── admin/        # 管理后台API
│   │   │   ├── auth.py       # 认证
│   │   │   ├── learning_paths.py  # 学习路线
│   │   │   ├── interview.py  # 面试题
│   │   │   ├── notes.py      # 笔记
│   │   │   └── ai_assistant.py # AI助手
│   │   ├── core/             # 核心模块
│   │   │   ├── config_manager.py  # 配置管理
│   │   │   ├── database.py   # 数据库
│   │   │   └── security.py   # 安全认证
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic Schemas
│   │   ├── services/         # 业务逻辑
│   │   │   ├── ai_assistant_service.py  # AI助手
│   │   │   ├── interview_simulator.py   # 面试模拟
│   │   │   ├── n8n_client.py           # n8n客户端
│   │   │   └── dynamic_resource_service.py  # 资源搜索
│   │   └── main.py           # 应用入口
│   ├── config.json           # 配置文件（本地）
│   ├── config.example.json   # 配置模板
│   ├── requirements.txt      # Python依赖
│   └── README.md            # 后端文档
├── frontend/                 # 前端应用
│   ├── src/
│   │   ├── api/             # API封装
│   │   ├── components/      # React组件
│   │   ├── pages/           # 页面
│   │   │   ├── HomePage.tsx
│   │   │   ├── LearningPathPage.tsx
│   │   │   ├── NotesPage.tsx
│   │   │   ├── AIAssistantPage.tsx
│   │   │   ├── MistakesPage.tsx
│   │   │   └── admin/       # 管理后台页面
│   │   ├── services/        # 服务层
│   │   ├── types/           # TypeScript类型
│   │   └── App.tsx          # 应用入口
│   ├── package.json         # 前端依赖
│   └── vite.config.ts       # Vite配置
├── start-all.sh             # 一键启动脚本
├── docker-compose.yml       # Docker配置
├── .gitignore              # Git忽略规则
└── README.md               # 项目文档
```

## 🔒 安全说明

- ✅ JWT认证机制
- ✅ 密码bcrypt加密
- ✅ API密钥配置文件保护（.gitignore）
- ✅ CORS跨域配置
- ✅ SQL注入防护（SQLAlchemy ORM）
- ✅ 操作日志审计

**重要提醒：**
- `config.json` 包含API密钥，**请勿提交到Git**
- 生产环境请使用HTTPS
- 定期更新JWT密钥

## 📊 数据库

使用SQLite作为默认数据库（开发环境），生产环境建议使用PostgreSQL。

主要数据表：
- `users` - 用户信息
- `learning_paths` - 学习路线
- `interview_questions` - 面试题库
- `question_status` - 答题状态
- `notes` - 笔记
- `notebooks` - 笔记本
- `chat_history` - AI对话历史
- `interview_sessions` - 面试会话

## 🐛 故障排除

### 常见问题

**1. AI助手报错 "NoneType and NoneType"**

已通过monkey patch修复第三方API兼容性问题。如仍出现，请检查：
- OpenAI API配置是否正确
- 网络连接是否正常

**2. n8n工作流调用失败**

检查：
- n8n服务是否正常运行
- `config.json` 中的 `webhook_url` 是否正确
- 工作流是否已激活

**3. 前端无法连接后端**

检查：
- 后端服务是否在8000端口运行
- CORS配置是否正确
- 浏览器开发者工具Network面板查看具体错误

## 📝 开发指南

### 添加新的API端点

1. 在 `backend/app/api/` 创建新路由文件
2. 在 `backend/app/main.py` 注册路由
3. 在 `frontend/src/services/` 创建对应的API封装
4. 在前端组件中调用

### 自定义AI提示词

编辑 `backend/app/services/ai_assistant_service.py` 中的 `system_prompt`

### 扩展工作流

在n8n中编辑工作流，导出JSON后替换项目中的工作流文件。

## 🚀 部署建议

### 开发环境
- 使用SQLite数据库
- 热重载开发

### 生产环境
- 使用PostgreSQL/MySQL
- 配置Nginx反向代理
- 启用HTTPS
- 使用PM2/Gunicorn管理进程
- 前端构建后通过CDN分发

```bash
# 前端构建
cd frontend && npm run build

# 后端生产启动
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 👥 致谢

- OpenAI - GPT模型
- LangChain - AI应用框架
- n8n - 工作流自动化
- FastAPI - 现代Python Web框架
- React - 前端UI框架
- Ant Design - UI组件库

---

**注意事项：**
- 本项目需要OpenAI API或兼容的第三方API
- 请遵守相关API的使用条款
- 生产环境使用前请进行充分测试

如有问题，请提交Issue或查看详细文档：`backend/README.md`
