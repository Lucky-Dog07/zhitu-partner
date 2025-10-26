#!/bin/bash

# 职途伴侣 - 一键启动脚本
# ================================

echo "🚀 启动职途伴侣应用"
echo "================================"
echo ""

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 启动Docker服务（PostgreSQL + n8n）
echo "📦 启动Docker服务..."
docker-compose up -d

echo "⏳ 等待数据库启动..."
sleep 5

# 初始化数据库（如果需要）
if [ -f "backend/init-schema.sql" ]; then
    echo "🗄️ 初始化数据库..."
    docker-compose exec -T postgres psql -U zhitu_user -d zhitu_db < backend/init-schema.sql 2>/dev/null || echo "数据库已存在"
fi

# 安装后端依赖（如果需要）
if [ ! -d "backend/venv" ]; then
    echo "📦 安装后端依赖..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# 启动后端
echo "🐍 启动后端服务..."
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 安装前端依赖（如果需要）
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

# 启动前端
echo "⚛️  启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ 所有服务已启动！"
echo "================================"
echo ""
echo "📍 访问地址："
echo "  - 前端应用: http://localhost:5173"
echo "  - 后端API: http://localhost:8000"
echo "  - API文档: http://localhost:8000/docs"
echo "  - n8n工作流: http://localhost:5678"
echo ""
echo "💡 按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "echo ''; echo '⏹️  停止所有服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker-compose down; echo '✅ 服务已停止'; exit 0" INT

wait

