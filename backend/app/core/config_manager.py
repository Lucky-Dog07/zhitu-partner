"""
配置管理服务
从config.json文件加载和管理系统配置
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载配置文件"""
        # 配置文件路径（backend目录下）
        backend_dir = Path(__file__).parent.parent.parent
        config_path = backend_dir / "config.json"
        example_path = backend_dir / "config.example.json"
        
        # 如果config.json不存在，从example复制
        if not config_path.exists():
            if example_path.exists():
                print(f"⚠️  配置文件不存在，从 {example_path} 创建默认配置...")
                import shutil
                shutil.copy(example_path, config_path)
                print(f"✅ 已创建配置文件: {config_path}")
                print("请修改 config.json 中的API密钥和其他配置！")
            else:
                raise FileNotFoundError(
                    f"配置文件不存在: {config_path}\n"
                    f"请在backend目录下创建 config.json 或 config.example.json"
                )
        
        # 加载配置
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            print(f"✅ 配置加载成功: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件JSON格式错误: {e}")
        except Exception as e:
            raise Exception(f"加载配置文件失败: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套键
        例如: get("openai.api_key")
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def get_openai_config(self) -> Dict[str, Any]:
        """获取OpenAI配置"""
        return self.get('openai', {})
    
    def get_n8n_config(self) -> Dict[str, Any]:
        """获取n8n配置"""
        return self.get('n8n', {})
    
    def get_database_url(self) -> str:
        """获取数据库URL"""
        return self.get('database.url', 'sqlite:///./app/zhitu.db')
    
    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        return self.get('security', {})
    
    def get_cors_origins(self) -> list:
        """获取CORS允许的源"""
        return self.get('app.cors_origins', ['http://localhost:5173'])
    
    def reload(self):
        """重新加载配置"""
        self._load_config()


# 创建全局配置实例
config = ConfigManager()

