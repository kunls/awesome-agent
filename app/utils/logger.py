"""
日志管理模块
提供统一的日志记录功能
"""

import logging
import sys
from functools import lru_cache
from typing import Optional

from .config import get_settings


class ColorFormatter(logging.Formatter):
    """
    彩色日志格式化器
    为不同级别的日志添加颜色
    """
    
    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
    }
    RESET = '\033[0m'

    def format(self, record):
        """格式化日志记录"""
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    use_colors: bool = True
) -> None:
    """
    设置日志配置
    
    Args:
        level: 日志级别
        format_string: 日志格式字符串
        use_colors: 是否使用彩色输出
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 设置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # 移除已有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # 选择格式化器
    if use_colors and sys.stdout.isatty():
        formatter = ColorFormatter(format_string)
    else:
        formatter = logging.Formatter(format_string)
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


@lru_cache()
def get_logger(name: str = __name__) -> logging.Logger:
    """
    获取日志记录器（带缓存）
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    settings = get_settings()
    
    # 如果还没有设置过日志，则进行初始化
    if not logging.getLogger().handlers:
        setup_logging(
            level=settings.log_level,
            use_colors=settings.is_development
        )
    
    return logging.getLogger(name)


class LoggerMixin:
    """
    日志记录器混入类
    为其他类提供日志记录功能
    """
    
    @property
    def logger(self) -> logging.Logger:
        """获取当前类的日志记录器"""
        return get_logger(self.__class__.__module__ + "." + self.__class__.__name__) 