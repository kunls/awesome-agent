"""
Awesome List 核心服务模块
整合搜索和LLM功能，实现完整的Awesome List生成流程
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from app.models import (
    GenerateAwesomeListRequest,
    GenerateAwesomeListResponse,
    SearchResults,
    ExtendedTopic
)
from app.services.search_service import SearchService
from app.services.llm_service import LLMService
from app.services.intelligent_search_service import IntelligentSearchService
from app.services.reranker_service import RerankerService
from app.utils import get_settings, get_logger, AwesomeAgentException, LoggerMixin


class AwesomeListService(LoggerMixin):
    """
    Awesome List 核心服务类
    负责协调搜索和AI生成，实现完整的工作流程
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.search_service = SearchService()
        self.llm_service = LLMService()
        self.intelligent_search_service = IntelligentSearchService()
        self.reranker_service = RerankerService()
    
    async def generate_awesome_list(
        self, 
        request: GenerateAwesomeListRequest
    ) -> GenerateAwesomeListResponse:
        """
        生成完整的Awesome List（传统搜索模式）
        流程：直接搜索用户关键词 → LLM整理成list
        
        Args:
            request: 生成请求
            
        Returns:
            GenerateAwesomeListResponse: 生成响应
        """
        start_time = datetime.now()
        self.logger.info(f"🚀 开始传统搜索模式，主题: {request.topic}")
        
        try:
            # 步骤1：直接搜索用户输入的关键词
            self.logger.info("📍 步骤1/3: 直接搜索用户关键词")
            search_results = await self.search_service.search_topic(
                topic=request.topic,
                max_results=request.max_results,
                search_depth="basic",
                academic_only=True
            )
            self.logger.info(f"✅ 搜索完成，找到 {len(search_results.results)} 个结果")

            # 步骤2：重排序优化
            self.logger.info(f"📍 步骤2/3: 应用重排序优化 (评分方法: {request.scoring_method})")
            search_results = await self.reranker_service.rerank_search_results(
                search_results=search_results,
                query=request.topic,
                target_count=request.max_results,
                scoring_method=request.scoring_method
            )
            
            # 步骤3：LLM整理成Awesome List
            self.logger.info("📍 步骤3/3: LLM整理搜索结果")
            awesome_list_content = await self.llm_service.generate_awesome_list(
                topic=request.topic,
                search_results=search_results,
                language=request.language,
                model=request.model
            )
            
            # 从生成内容中提取关键词
            keywords = await self.llm_service.extract_keywords(
                text=awesome_list_content,
                max_keywords=8
            )
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            model_used = self._get_model_display_name(request.model)
            
            self.logger.info(
                f"🎉 传统搜索模式完成！"
                f"总耗时: {processing_time:.2f}s，"
                f"搜索结果: {search_results.total_count}个，"
                f"关键词: {len(keywords)}个"
            )
            
            return GenerateAwesomeListResponse(
                awesome_list=awesome_list_content,
                keywords=keywords,
                total_results=search_results.total_count,
                processing_time=processing_time,
                model_used=model_used
            )
            
        except Exception as e:
            self.logger.error(f"❌ 传统搜索模式失败: {e}", exc_info=True)
            raise AwesomeAgentException(f"生成Awesome List失败: {str(e)}")
    
    async def generate_awesome_list_intelligent(
        self, 
        request: GenerateAwesomeListRequest
    ) -> GenerateAwesomeListResponse:
        """
        智能生成Awesome List（智能搜索模式）
        流程：LLM扩展主题 → Function Calling搜索各个扩展主题 → 整理成list
        
        Args:
            request: 生成请求
            
        Returns:
            GenerateAwesomeListResponse: 生成响应
        """
        start_time = datetime.now()
        self.logger.info(f"🤖 开始智能搜索模式，主题: {request.topic}")
        
        try:
            # 步骤1：LLM扩展主题
            self.logger.info("📍 步骤1/4: LLM分析并扩展主题")
            extended_topic = await self.llm_service.expand_topic(
                topic=request.topic,
                language=request.language
            )
            
            # 步骤2：使用Function Calling搜索各个扩展主题
            self.logger.info("📍 步骤2/4: Function Calling搜索扩展主题")
            search_results = await self.intelligent_search_service.intelligent_search_with_topics(
                original_topic=request.topic,
                extended_topic=extended_topic,
                language=request.language,
                model=request.model,
                max_results=request.max_results
            )
            self.logger.info(f"✅ 智能搜索完成，找到 {len(search_results.results)} 个结果")

            # 步骤3：重排序优化
            self.logger.info(f"📍 步骤3/4: 应用重排序优化 (评分方法: {request.scoring_method})")
            search_results = await self.reranker_service.rerank_search_results(
                search_results=search_results,
                query=request.topic,
                target_count=request.max_results,
                scoring_method=request.scoring_method
            )
            
            # 步骤4：LLM整理成Awesome List
            self.logger.info("📍 步骤4/4: LLM整理搜索结果")
            awesome_list_content = await self.llm_service.generate_awesome_list(
                topic=request.topic,
                search_results=search_results,
                language=request.language,
                model=request.model
            )
            
            # 使用扩展主题的丰富关键词信息
            all_keywords = set()
            all_keywords.update(extended_topic.extended_keywords)
            all_keywords.update(extended_topic.related_concepts)
            
            # 从生成内容中补充关键词
            content_keywords = await self.llm_service.extract_keywords(
                text=awesome_list_content,
                max_keywords=3
            )
            all_keywords.update(content_keywords)
            
            # 清理并限制关键词数量
            keywords = [kw.strip() for kw in all_keywords if kw and len(kw.strip()) > 1][:10]
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            model_used = self._get_model_display_name(request.model)
            
            self.logger.info(
                f"🎉 智能搜索模式完成！"
                f"总耗时: {processing_time:.2f}s，"
                f"搜索结果: {search_results.total_count}个，"
                f"关键词: {len(keywords)}个"
            )
            
            return GenerateAwesomeListResponse(
                awesome_list=awesome_list_content,
                keywords=keywords,
                total_results=search_results.total_count,
                processing_time=processing_time,
                model_used=model_used
            )
            
        except Exception as e:
            self.logger.error(f"❌ 智能搜索模式失败: {e}", exc_info=True)
            raise AwesomeAgentException(f"智能生成Awesome List失败: {str(e)}")
    
    def _get_model_display_name(self, model: str) -> str:
        """
        获取模型的显示名称
        """
        model_names = {
            "gpt": "GPT-4-Turbo",  # 更新为GPT-4
            "deepseek": "DeepSeek-Chat"
        }
        
        if model and model.lower() in model_names:
            return model_names[model.lower()]
        
        # 使用默认模型
        default_model = self.settings.default_llm_model.lower()
        return model_names.get(default_model, "GPT-4-Turbo")
    
    async def get_search_preview(self, topic: str, max_results: int = 5) -> SearchResults:
        """
        获取搜索预览（用于调试或预览功能）
        
        Args:
            topic: 搜索主题
            max_results: 最大结果数
            
        Returns:
            SearchResults: 搜索结果
        """
        self.logger.info(f"获取搜索预览: {topic}")
        
        try:
            return await self.search_service.search_topic(
                topic=topic,
                max_results=max_results,
                search_depth="basic",
                academic_only=True
            )
        except Exception as e:
            self.logger.error(f"搜索预览失败: {e}")
            raise AwesomeAgentException(f"搜索预览失败: {str(e)}")
    
    async def test_llm_connection(self, model: str = None) -> Dict[str, Any]:
        """
        测试LLM连接（用于调试）
        
        Args:
            model: 要测试的模型
            
        Returns:
            Dict[str, Any]: 测试结果
        """
        test_model = model or self.settings.default_llm_model
        self.logger.info(f"测试LLM连接: {test_model}")
        
        try:
            start_time = datetime.now()
            
            response = await self.llm_service._call_llm(
                model=test_model,
                prompt="请简单回复'连接测试成功'",
                max_tokens=50,
                temperature=0.1
            )
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "status": "success",
                "model": test_model,
                "response": response,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"LLM连接测试失败: {e}")
            return {
                "status": "failed",
                "model": test_model,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            } 