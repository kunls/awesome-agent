"""
配置管理模块
处理环境变量和应用配置
"""

import os
from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用配置类
    从环境变量中读取配置信息
    """
    
    # API Keys
    openai_api_key: str = Field(
        ...,
        env="OPENAI_API_KEY",
        description="OpenAI API密钥"
    )
    
    deepseek_api_key: str = Field(
        ..., 
        env="DEEPSEEK_API_KEY",
        description="DeepSeek API密钥"
    )
    
    tavily_api_key: str = Field(
        ...,
        env="TAVILY_API_KEY", 
        description="Tavily API密钥"
    )
    
    # Application Settings
    environment: str = Field(
        default="development",
        env="ENVIRONMENT",
        description="运行环境"
    )
    
    default_llm_model: str = Field(
        default="gpt",
        env="DEFAULT_LLM_MODEL",
        description="默认使用的大语言模型"
    )
    
    max_search_results: int = Field(
        default=10,
        env="MAX_SEARCH_RESULTS",
        description="搜索结果的最大数量"
    )
    
    request_timeout: int = Field(
        default=60,
        env="REQUEST_TIMEOUT",
        description="请求超时时间（秒）"
    )
    
    # Server Settings
    host: str = Field(
        default="0.0.0.0",
        env="HOST",
        description="服务器监听地址"
    )
    
    port: int = Field(
        default=8000,
        env="PORT",
        description="服务器端口"
    )
    
    # Debug Settings
    debug: bool = Field(
        default=False,
        env="DEBUG",
        description="是否启用调试模式"
    )
    
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="日志级别"
    )

    class Config:
        """Pydantic配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def is_development(self) -> bool:
        """检查是否为开发环境"""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """检查是否为生产环境"""
        return self.environment.lower() == "production"
    
    def get_openai_config(self) -> dict:
        """获取OpenAI配置"""
        return {
            "api_key": self.openai_api_key,
            "timeout": self.request_timeout
        }
    
    def get_deepseek_config(self) -> dict:
        """获取DeepSeek配置"""
        return {
            "api_key": self.deepseek_api_key,
            "timeout": self.request_timeout
        }
    
    def get_tavily_config(self) -> dict:
        """获取Tavily配置"""
        return {
            "api_key": self.tavily_api_key,
            "max_results": self.max_search_results
        }


@lru_cache()
def get_settings() -> Settings:
    """
    获取应用配置（带缓存）
    
    Returns:
        Settings: 应用配置实例
    """
    return Settings() 