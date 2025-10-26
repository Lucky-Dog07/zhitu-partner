#!/bin/bash

# 职途伴侣 - 快速配置脚本

echo "======================================="
echo "   职途伴侣后端 - 配置向导"
echo "======================================="
echo ""

# 检查是否存在config.json
if [ -f "config.json" ]; then
    echo "⚠️  检测到已存在 config.json"
    read -p "是否覆盖现有配置？(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✅ 保持现有配置"
        python check_config.py
        exit 0
    fi
fi

# 复制模板
echo "📋 创建配置文件..."
cp config.example.json config.json
echo "✅ 已创建 config.json"
echo ""

# 交互式配置
echo "请输入以下配置信息（直接回车使用默认值）："
echo ""

# OpenAI API Key
read -p "🤖 OpenAI API Key: " openai_key
if [ ! -z "$openai_key" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|your-openai-api-key-here|$openai_key|g" config.json
    else
        # Linux
        sed -i "s|your-openai-api-key-here|$openai_key|g" config.json
    fi
fi

# n8n Webhook URL
read -p "🔗 n8n Webhook URL [http://localhost:5678/webhook/zhitu-learning]: " n8n_url
if [ ! -z "$n8n_url" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|your-n8n-webhook-url-here|$n8n_url|g" config.json
    else
        sed -i "s|your-n8n-webhook-url-here|$n8n_url|g" config.json
    fi
fi

# Secret Key
read -p "🔒 JWT Secret Key [随机生成]: " secret_key
if [ -z "$secret_key" ]; then
    # 生成随机密钥
    secret_key=$(openssl rand -hex 32 2>/dev/null || python -c "import secrets; print(secrets.token_hex(32))")
fi
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|your-secret-key-here-please-change-this|$secret_key|g" config.json
else
    sed -i "s|your-secret-key-here-please-change-this|$secret_key|g" config.json
fi

echo ""
echo "======================================="
echo "✅ 配置完成！"
echo "======================================="
echo ""

# 显示配置
python check_config.py

echo ""
echo "📝 提示："
echo "  - 配置文件位置: $(pwd)/config.json"
echo "  - 修改配置: vim config.json"
echo "  - 检查配置: python check_config.py"
echo "  - 启动服务: python -m uvicorn app.main:app --reload"
echo ""

