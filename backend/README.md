# 职途伴侣 - 后端服务

基于 FastAPI 的智能职业规划助手后端服务。

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置系统

**重要：首次运行前必须配置！**

复制配置模板并填写您的API密钥：

```bash
cp config.example.json config.json
```

编辑 `config.json` 文件，填写以下配置：

```json
{
  "openai": {
    "api_key": "your-openai-api-key-here",  // ⚠️ 必填！
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "n8n": {
    "webhook_url": "http://localhost:5678/webhook/learning-path",  // ⚠️ 必填！
    "timeout": 120
  },
  "database": {
    "url": "sqlite:///./app/zhitu.db"
  },
  "security": {
    "secret_key": "your-secret-key-here",  // ⚠️ 修改为随机字符串！
    "algorithm": "HS256",
    "access_token_expire_minutes": 43200
  }
}
```

**配置说明：**

- **openai.api_key**: OpenAI API密钥（可从 https://platform.openai.com/api-keys 获取）
- **openai.base_url**: API基础URL（如使用第三方代理可修改）
- **n8n.webhook_url**: n8n工作流Webhook完整URL
- **security.secret_key**: JWT加密密钥（建议使用随机生成的长字符串）

### 3. 初始化数据库

```bash
# 运行数据库迁移
python -m alembic upgrade head

# 创建管理员账号（可选）
python create_admin.py
```

### 4. 启动服务

```bash
# 开发模式（自动重载）
python -m uvicorn app.main:app --reload --port 8000

# 生产模式（后台运行）
nohup python -m uvicorn app.main:app --port 8000 > backend.log 2>&1 &
```

服务将在 http://localhost:8000 启动

- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 项目结构

```
backend/
├── app/
│   ├── api/              # API路由
│   │   ├── admin/        # 管理后台API
│   │   ├── auth.py       # 认证API
│   │   ├── learning_paths.py
│   │   ├── notes.py
│   │   └── ...
│   ├── core/             # 核心模块
│   │   ├── config_manager.py  # 配置管理器 ⚠️ 新增
│   │   ├── config.py     # 旧配置（已废弃）
│   │   ├── database.py
│   │   └── security.py
│   ├── models/           # 数据模型
│   ├── services/         # 业务逻辑
│   │   ├── ai_assistant_service.py  # AI助手
│   │   ├── interview_simulator.py   # 面试模拟
│   │   ├── n8n_client.py            # n8n客户端
│   │   └── ...
│   └── main.py           # 应用入口
├── config.json           # 配置文件（不提交到Git）⚠️ 必须创建
├── config.example.json   # 配置模板
├── requirements.txt      # Python依赖
└── README.md
```

## 安全注意事项

⚠️ **重要：请勿将 `config.json` 提交到版本控制系统！**

`config.json` 文件包含敏感信息（API密钥、密码等），已被添加到 `.gitignore`。

如需分享配置结构，请使用 `config.example.json` 模板。

## 常见问题

### 1. 启动时提示"配置文件不存在"

**原因**：未创建 `config.json` 文件

**解决方案**：
```bash
cp config.example.json config.json
# 然后编辑 config.json 填写您的API密钥
```

### 2. OpenAI API调用失败

**原因**：API密钥未配置或不正确

**解决方案**：
- 检查 `config.json` 中的 `openai.api_key` 是否正确
- 确认API密钥有效且有足够余额
- 检查 `openai.base_url` 是否正确

### 3. n8n工作流调用失败

**原因**：Webhook URL未配置

**解决方案**：
- 确保n8n服务正在运行
- 检查 `config.json` 中的 `n8n.webhook_url` 是否正确
- 测试Webhook是否可访问

## 开发指南

### 添加新的配置项

1. 在 `config.example.json` 中添加新配置项及说明
2. 在 `app/core/config_manager.py` 中添加相应的getter方法
3. 更新 `README.md` 中的配置说明

### 使用配置

```python
from app.core.config_manager import config

# 获取配置
openai_config = config.get_openai_config()
api_key = openai_config.get('api_key')

# 或使用点号访问
api_key = config.get('openai.api_key')
```

## 技术栈

- **框架**: FastAPI
- **AI**: LangChain + OpenAI
- **数据库**: SQLAlchemy + SQLite/PostgreSQL
- **认证**: JWT
- **工作流**: n8n

## 许可证

MIT License

