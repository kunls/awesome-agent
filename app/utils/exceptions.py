"""
自定义异常类模块
定义项目中使用的所有自定义异常
"""

from typing import Optional, Dict, Any


class AwesomeAgentException(Exception):
    """
    Awesome Agent 基础异常类
    所有自定义异常的基类
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化异常
        
        Args:
            message: 错误信息
            error_code: 错误代码
            details: 错误详细信息
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class ConfigException(AwesomeAgentException):
    """
    配置相关异常
    当配置文件或环境变量有问题时抛出
    """
    pass


class SearchException(AwesomeAgentException):
    """
    搜索相关异常
    当搜索操作失败时抛出
    """
    pass


class LLMException(AwesomeAgentException):
    """
    大语言模型相关异常
    当LLM调用失败时抛出
    """
    pass


class ValidationException(AwesomeAgentException):
    """
    数据验证异常
    当输入数据验证失败时抛出
    """
    pass


class RateLimitException(AwesomeAgentException):
    """
    API速率限制异常
    当API调用达到速率限制时抛出
    """
    pass


class TimeoutException(AwesomeAgentException):
    """
    超时异常
    当操作超时时抛出
    """
    pass


class APIException(AwesomeAgentException):
    """
    API调用异常
    当第三方API调用失败时抛出
    """
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        初始化API异常
        
        Args:
            message: 错误信息
            status_code: HTTP状态码
            response_data: 响应数据
            **kwargs: 其他参数
        """
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_data = response_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = super().to_dict()
        result.update({
            "status_code": self.status_code,
            "response_data": self.response_data
        })
        return result 