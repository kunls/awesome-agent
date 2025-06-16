"""
API响应数据模型
定义所有API接口的响应格式模型
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class GenerateAwesomeListResponse(BaseModel):
    """
    生成Awesome List的响应模型
    """
    
    awesome_list: str = Field(
        ...,
        description="生成的Markdown格式的Awesome List内容",
        example="# Awesome Vue.js\n\n## 框架\n- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架"
    )
    
    keywords: List[str] = Field(
        ...,
        description="从主题中提取的关键词列表",
        example=["Vue.js", "前端框架", "JavaScript", "组件化"]
    )
    
    total_results: int = Field(
        ...,
        description="搜索到的结果总数",
        ge=0,
        example=25
    )
    
    processing_time: float = Field(
        ...,
        description="处理耗时（秒）",
        ge=0,
        example=12.5
    )
    
    model_used: str = Field(
        ...,
        description="实际使用的大语言模型",
        example="gpt-4-turbo"
    )

    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "awesome_list": "# Awesome Vue.js\n\n## 官方资源\n- [Vue.js 官网](https://vuejs.org/)\n\n## 学习资源\n- [Vue.js 官方教程](https://vuejs.org/tutorial/)",
                "keywords": ["Vue.js", "前端", "JavaScript", "组件化", "响应式"],
                "total_results": 25,
                "processing_time": 12.5,
                "model_used": "gpt-4-turbo"
            }
        }


class HealthCheckResponse(BaseModel):
    """
    健康检查响应模型
    """
    
    status: str = Field(
        ...,
        description="服务状态",
        example="healthy"
    )
    
    message: str = Field(
        ...,
        description="状态描述信息",
        example="Awesome List Agent is running normally"
    )
    
    version: str = Field(
        ...,
        description="应用版本",
        example="0.1.0"
    )
    
    timestamp: str = Field(
        ...,
        description="检查时间戳",
        example="2024-12-19T10:30:00Z"
    )

    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "Awesome List Agent is running normally",
                "version": "0.1.0",
                "timestamp": "2024-12-19T10:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """
    错误响应模型
    """
    
    error: str = Field(
        ...,
        description="错误类型",
        example="ValidationError"
    )
    
    message: str = Field(
        ...,
        description="错误详细信息",
        example="主题不能为空"
    )
    
    details: Optional[dict] = Field(
        default=None,
        description="错误详细信息（可选）",
        example={"field": "topic", "issue": "字段不能为空"}
    )
    
    timestamp: str = Field(
        ...,
        description="错误发生时间",
        example="2024-12-19T10:30:00Z"
    )

    class Config:
        """Pydantic配置"""
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "请求参数验证失败",
                "details": {"topic": "主题不能为空"},
                "timestamp": "2024-12-19T10:30:00Z"
            }
        } 