"""
API请求数据模型
定义所有API接口的请求参数模型
"""

from typing import Optional
from pydantic import BaseModel, Field


class GenerateAwesomeListRequest(BaseModel):
    """
    生成Awesome List的请求模型
    """
    
    topic: str = Field(
        ...,
        description="用户输入的主题，用于生成相关的Awesome List",
        min_length=1,
        max_length=200,
        example="人工智能"
    )
    
    model: Optional[str] = Field(
        default="gpt",
        description="指定使用的大语言模型 (gpt 或 deepseek)",
        pattern="^(gpt|deepseek)$",
        example="gpt"
    )
    
    max_results: Optional[int] = Field(
        default=10,
        alias="maxResults",  # 支持前端的驼峰式命名
        description="搜索结果的最大数量",
        ge=1,
        le=50,
        example=10
    )
    
    language: Optional[str] = Field(
        default="zh",
        description="生成内容的语言 (zh: 中文, en: 英文)",
        pattern="^(zh|en)$",
        example="zh"
    )
    
    scoring_method: Optional[str] = Field(
        default="rule_based",
        description="重排序评分方法 (rule_based: 基于规则, llm_based: 基于大模型)",
        pattern="^(rule_based|llm_based)$",
        example="rule_based"
    )

    class Config:
        """Pydantic配置"""
        populate_by_name = True  # 允许使用字段名和别名
        json_schema_extra = {
            "example": {
                "topic": "Vue.js 前端开发",
                "model": "gpt",
                "max_results": 15,
                "language": "zh",
                "scoring_method": "rule_based"
            }
        } 