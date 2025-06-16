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
        生成完整的Awesome List
        
        Args:
            request: 生成请求
            
        Returns:
            GenerateAwesomeListResponse: 生成响应
        """
        start_time = datetime.now()
        self.logger.info(f"开始生成Awesome List，主题: {request.topic}")
        
        try:
            # 第一步：主题扩展
            self.logger.info("步骤1: 主题扩展")
            extended_topic = await self.llm_service.expand_topic(
                topic=request.topic,
                language=request.language
            )
            
            # 第二步：智能搜索
            self.logger.info("步骤2: 执行智能搜索（学术模式）")
            search_results = await self.search_service.search_topic(
                topic=request.topic,
                max_results=request.max_results,
                search_depth="basic",
                academic_only=True
            )
            
            # 第二步半：重排序优化
            self.logger.info(f"步骤2.5: 应用Reranker RAG优化排序 (评分方法: {request.scoring_method})")
            search_results = await self.reranker_service.rerank_search_results(
                search_results=search_results,
                query=request.topic,
                target_count=request.max_results,
                scoring_method=request.scoring_method
            )
            
            # 如果搜索结果不足，使用扩展查询再次搜索
            if len(search_results.results) < request.max_results // 2:
                self.logger.info("搜索结果不足，使用扩展查询")
                additional_results = await self._search_with_extended_queries(
                    extended_topic,
                    remaining_count=request.max_results - len(search_results.results)
                )
                
                # 合并搜索结果
                search_results = self._merge_search_results(
                    search_results, 
                    additional_results
                )
            
            # 第三步：生成Awesome List
            self.logger.info("步骤3: 生成Awesome List内容")
            awesome_list_content = await self.llm_service.generate_awesome_list(
                topic=request.topic,
                search_results=search_results,
                language=request.language,
                model=request.model
            )
            
            # 第四步：提取关键词
            self.logger.info("步骤4: 提取关键词")
            keywords = await self._extract_final_keywords(
                extended_topic,
                search_results,
                awesome_list_content
            )
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 确定使用的模型
            model_used = self._get_model_display_name(request.model)
            
            self.logger.info(
                f"Awesome List生成完成，总耗时: {processing_time:.2f}s，"
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
            self.logger.error(f"生成Awesome List失败: {e}", exc_info=True)
            raise AwesomeAgentException(f"生成Awesome List失败: {str(e)}")
    
    async def generate_awesome_list_intelligent(
        self, 
        request: GenerateAwesomeListRequest
    ) -> GenerateAwesomeListResponse:
        """
        使用Function Calling智能生成Awesome List
        让大模型自主决定搜索策略
        
        Args:
            request: 生成请求
            
        Returns:
            GenerateAwesomeListResponse: 生成响应
        """
        start_time = datetime.now()
        self.logger.info(f"开始智能生成Awesome List，主题: {request.topic}")
        
        try:
            # 第一步：智能搜索，让大模型自主决定搜索策略
            self.logger.info("步骤1: 智能搜索（大模型自主决策）")
            search_results = await self.intelligent_search_service.intelligent_search(
                topic=request.topic,
                language=request.language,
                model=request.model
            )
            
            # 第一步半：智能重排序
            self.logger.info(f"步骤1.5: 应用Reranker RAG智能优化 (评分方法: {request.scoring_method})")
            search_results = await self.reranker_service.rerank_search_results(
                search_results=search_results,
                query=request.topic,
                target_count=request.max_results,
                scoring_method=request.scoring_method
            )
            
            # 如果智能搜索结果不足，补充传统搜索
            if len(search_results.results) < request.max_results // 2:
                self.logger.info("智能搜索结果不足，补充传统搜索")
                additional_results = await self.search_service.search_topic(
                    topic=request.topic,
                    max_results=request.max_results - len(search_results.results),
                    search_depth="basic",
                    academic_only=True
                )
                
                # 合并搜索结果
                search_results = self._merge_search_results(
                    search_results, 
                    additional_results
                )
            
            # 第二步：生成Awesome List
            self.logger.info("步骤2: 生成Awesome List内容")
            awesome_list_content = await self.llm_service.generate_awesome_list(
                topic=request.topic,
                search_results=search_results,
                language=request.language,
                model=request.model
            )
            
            # 第三步：提取关键词
            self.logger.info("步骤3: 提取关键词")
            keywords = await self._extract_keywords_from_results(
                search_results,
                awesome_list_content
            )
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # 确定使用的模型
            model_used = self._get_model_display_name(request.model)
            
            self.logger.info(
                f"智能Awesome List生成完成，总耗时: {processing_time:.2f}s，"
                f"搜索结果: {search_results.total_count}个，"
                f"关键词: {len(keywords)}个，"
                f"搜索调用: {search_results.filters_applied.get('search_calls', 0)}次"
            )
            
            return GenerateAwesomeListResponse(
                awesome_list=awesome_list_content,
                keywords=keywords,
                total_results=search_results.total_count,
                processing_time=processing_time,
                model_used=model_used + " (智能搜索)"
            )
            
        except Exception as e:
            self.logger.error(f"智能生成Awesome List失败: {e}", exc_info=True)
            raise AwesomeAgentException(f"智能生成Awesome List失败: {str(e)}")
    
    async def _extract_keywords_from_results(
        self,
        search_results: SearchResults,
        awesome_list_content: str
    ) -> List[str]:
        """
        从搜索结果和生成内容中提取关键词
        """
        # 合并所有可能的关键词来源
        all_keywords = set()
        
        # 来源1: 从搜索结果中提取
        search_text = " ".join([
            result.title + " " + result.content 
            for result in search_results.results[:5]
        ])
        
        try:
            extracted_keywords = await self.llm_service.extract_keywords(
                text=search_text,
                max_keywords=6
            )
            all_keywords.update(extracted_keywords)
        except Exception as e:
            self.logger.warning(f"从搜索结果提取关键词失败: {e}")
        
        # 来源2: 从生成的内容中提取
        try:
            content_keywords = await self.llm_service.extract_keywords(
                text=awesome_list_content,
                max_keywords=4
            )
            all_keywords.update(content_keywords)
        except Exception as e:
            self.logger.warning(f"从生成内容提取关键词失败: {e}")
        
        # 清理和过滤关键词
        filtered_keywords = []
        for keyword in all_keywords:
            if keyword and len(keyword.strip()) > 1:
                cleaned = keyword.strip()
                if cleaned not in filtered_keywords:
                    filtered_keywords.append(cleaned)
        
        # 返回前10个关键词
        return filtered_keywords[:10]
    
    async def _search_with_extended_queries(
        self,
        extended_topic: ExtendedTopic,
        remaining_count: int
    ) -> SearchResults:
        """
        使用扩展查询进行额外搜索
        """
        self.logger.info("使用扩展查询进行补充搜索")
        
        all_results = []
        
        # 使用扩展的搜索查询
        for query in extended_topic.search_queries[:3]:  # 限制查询数量
            try:
                results = await self.search_service.search_topic(
                    topic=query,
                    max_results=max(2, remaining_count // len(extended_topic.search_queries)),
                    search_depth="basic",
                    academic_only=True
                )
                all_results.extend(results.results)
                
                # 避免API限制
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.warning(f"扩展查询 '{query}' 失败: {e}")
                continue
        
        # 去重
        unique_results = self.search_service._deduplicate_results(all_results)
        
        return SearchResults(
            query=f"Extended search for {extended_topic.original_topic}",
            results=unique_results[:remaining_count],
            total_count=len(unique_results),
            search_time=0,
            filters_applied={"type": "extended_search"}
        )
    
    def _merge_search_results(
        self,
        primary_results: SearchResults,
        additional_results: SearchResults
    ) -> SearchResults:
        """
        合并多个搜索结果
        """
        combined_results = primary_results.results + additional_results.results
        
        # 去重
        unique_results = self.search_service._deduplicate_results(combined_results)
        
        return SearchResults(
            query=primary_results.query,
            results=unique_results,
            total_count=len(unique_results),
            search_time=primary_results.search_time + additional_results.search_time,
            filters_applied={
                **primary_results.filters_applied,
                "merged_with_extended": True
            }
        )
    
    async def _extract_final_keywords(
        self,
        extended_topic: ExtendedTopic,
        search_results: SearchResults,
        awesome_list_content: str
    ) -> List[str]:
        """
        提取最终的关键词列表
        """
        # 合并所有可能的关键词来源
        all_keywords = set()
        
        # 来源1: 扩展主题的关键词
        all_keywords.update(extended_topic.extended_keywords)
        
        # 来源2: 相关概念
        all_keywords.update(extended_topic.related_concepts)
        
        # 来源3: 从搜索结果中提取
        search_text = " ".join([
            result.title + " " + result.content 
            for result in search_results.results[:5]
        ])
        
        try:
            extracted_keywords = await self.llm_service.extract_keywords(
                text=search_text,
                max_keywords=5
            )
            all_keywords.update(extracted_keywords)
        except Exception as e:
            self.logger.warning(f"从搜索结果提取关键词失败: {e}")
        
        # 来源4: 从生成的内容中提取
        try:
            content_keywords = await self.llm_service.extract_keywords(
                text=awesome_list_content,
                max_keywords=3
            )
            all_keywords.update(content_keywords)
        except Exception as e:
            self.logger.warning(f"从生成内容提取关键词失败: {e}")
        
        # 清理和过滤关键词
        filtered_keywords = []
        for keyword in all_keywords:
            if keyword and len(keyword.strip()) > 1:
                cleaned = keyword.strip()
                if cleaned not in filtered_keywords:
                    filtered_keywords.append(cleaned)
        
        # 返回前10个关键词
        return filtered_keywords[:10]
    
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