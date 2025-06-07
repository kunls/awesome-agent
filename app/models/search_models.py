"""
搜索相关数据模型
定义搜索结果和搜索过程中使用的数据结构
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class SearchResult(BaseModel):
    """
    单个搜索结果模型
    """
    
    title: str = Field(
        ...,
        description="搜索结果标题",
        example="Vue.js - The Progressive JavaScript Framework"
    )
    
    url: HttpUrl = Field(
        ...,
        description="搜索结果链接",
        example="https://vuejs.org/"
    )
    
    content: str = Field(
        ...,
        description="搜索结果内容摘要",
        example="Vue.js is a progressive framework for building user interfaces..."
    )
    
    score: float = Field(
        ...,
        description="搜索结果相关性评分 (0-1)",
        ge=0,
        le=1,
        example=0.95
    )
    
    source: str = Field(
        ...,
        description="搜索结果来源类型",
        example="official"
    )
    
    published_date: Optional[str] = Field(
        default=None,
        description="发布时间",
        example="2023-12-01"
    )

    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "title": "Vue.js 官方文档",
                "url": "https://vuejs.org/guide/",
                "content": "Vue.js 是一套用于构建用户界面的渐进式JavaScript框架...",
                "score": 0.95,
                "source": "official",
                "published_date": "2023-12-01"
            }
        }


class SearchResults(BaseModel):
    """
    搜索结果集合模型
    """
    
    query: str = Field(
        ...,
        description="搜索查询词",
        example="Vue.js 前端框架"
    )
    
    results: List[SearchResult] = Field(
        ...,
        description="搜索结果列表",
        example=[]
    )
    
    total_count: int = Field(
        ...,
        description="搜索结果总数",
        ge=0,
        example=25
    )
    
    search_time: float = Field(
        ...,
        description="搜索耗时（秒）",
        ge=0,
        example=2.5
    )
    
    filters_applied: Dict[str, Any] = Field(
        default_factory=dict,
        description="应用的搜索过滤器",
        example={"language": "zh", "date_range": "2023-2024"}
    )

    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "query": "Vue.js 前端开发",
                "results": [
                    {
                        "title": "Vue.js 官方文档",
                        "url": "https://vuejs.org/",
                        "content": "Vue.js 渐进式JavaScript框架",
                        "score": 0.95,
                        "source": "official",
                        "published_date": "2023-12-01"
                    }
                ],
                "total_count": 1,
                "search_time": 2.5,
                "filters_applied": {"language": "zh"}
            }
        }


class ExtendedTopic(BaseModel):
    """
    扩展主题模型
    用于主题扩展和关键词生成
    """
    
    original_topic: str = Field(
        ...,
        description="原始主题",
        example="Vue.js"
    )
    
    extended_keywords: List[str] = Field(
        ...,
        description="扩展的关键词列表",
        example=["Vue.js", "前端框架", "JavaScript", "组件化", "响应式"]
    )
    
    related_concepts: List[str] = Field(
        ...,
        description="相关概念列表",
        example=["单页应用", "虚拟DOM", "组件生命周期"]
    )
    
    search_queries: List[str] = Field(
        ...,
        description="生成的搜索查询列表",
        example=[
            "Vue.js 官方文档",
            "Vue.js 最佳实践",
            "Vue.js 组件库"
        ]
    )

    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "original_topic": "Vue.js",
                "extended_keywords": ["Vue.js", "前端框架", "JavaScript"],
                "related_concepts": ["组件化", "响应式", "单页应用"],
                "search_queries": [
                    "Vue.js 官方文档",
                    "Vue.js 教程",
                    "Vue.js 组件库"
                ]
            }
        } 