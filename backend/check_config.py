#!/usr/bin/env python
"""
配置查看工具
用于查看当前配置（隐藏敏感信息）
"""
import json
from pathlib import Path


def mask_sensitive(value: str, show_chars: int = 8) -> str:
    """隐藏敏感信息，只显示前几个字符"""
    if not value or len(value) <= show_chars:
        return "***"
    return f"{value[:show_chars]}...***"


def main():
    config_path = Path(__file__).parent / "config.json"
    
    if not config_path.exists():
        print("❌ 配置文件不存在: config.json")
        print("请运行: cp config.example.json config.json")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("\n" + "="*60)
    print("📋 当前配置信息")
    print("="*60)
    
    # OpenAI配置
    print("\n🤖 OpenAI配置:")
    openai = config.get('openai', {})
    print(f"  API Key: {mask_sensitive(openai.get('api_key', ''))}")
    print(f"  Base URL: {openai.get('base_url', 'N/A')}")
    print(f"  Model: {openai.get('model', 'N/A')}")
    print(f"  Temperature: {openai.get('temperature', 'N/A')}")
    print(f"  Max Tokens: {openai.get('max_tokens', 'N/A')}")
    
    # n8n配置
    print("\n🔗 n8n配置:")
    n8n = config.get('n8n', {})
    print(f"  Webhook URL: {n8n.get('webhook_url', 'N/A')}")
    print(f"  Timeout: {n8n.get('timeout', 'N/A')}s")
    
    # 数据库配置
    print("\n💾 数据库配置:")
    db = config.get('database', {})
    print(f"  Database URL: {db.get('url', 'N/A')}")
    
    # 应用配置
    print("\n⚙️  应用配置:")
    app = config.get('app', {})
    print(f"  Name: {app.get('name', 'N/A')}")
    print(f"  Version: {app.get('version', 'N/A')}")
    print(f"  Debug: {app.get('debug', 'N/A')}")
    cors_origins = app.get('cors_origins', [])
    print(f"  CORS Origins: {len(cors_origins)} 个")
    for origin in cors_origins:
        print(f"    - {origin}")
    
    # 安全配置
    print("\n🔒 安全配置:")
    security = config.get('security', {})
    print(f"  Secret Key: {mask_sensitive(security.get('secret_key', ''))}")
    print(f"  Algorithm: {security.get('algorithm', 'N/A')}")
    print(f"  Token Expire: {security.get('access_token_expire_minutes', 'N/A')} 分钟")
    
    print("\n" + "="*60)
    print("✅ 配置检查完成")
    print("="*60 + "\n")
    
    # 检查是否有默认值未修改
    warnings = []
    if 'your-openai-api-key-here' in openai.get('api_key', ''):
        warnings.append("⚠️  OpenAI API Key 未配置")
    if 'your-n8n-webhook-url-here' in n8n.get('webhook_url', ''):
        warnings.append("⚠️  n8n Webhook URL 未配置")
    if 'your-secret-key-here' in security.get('secret_key', ''):
        warnings.append("⚠️  Secret Key 未修改（建议使用随机字符串）")
    
    if warnings:
        print("⚠️  警告：")
        for warning in warnings:
            print(f"  {warning}")
        print()


if __name__ == "__main__":
    main()

