"""
智能搜索服务模块
使用Function Calling让大模型自主决定搜索策略
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models import SearchResults, SearchResult
from app.services.search_service import SearchService
from app.services.llm_service import LLMService
from app.utils import get_settings, LoggerMixin, SearchException


class IntelligentSearchService(LoggerMixin):
    """
    智能搜索服务类
    使用Function Calling让大模型自主决定搜索策略
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.search_service = SearchService()
        self.llm_service = LLMService()
        
        # 定义搜索工具
        self.search_tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "搜索互联网获取相关资源和信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询关键词"
                            },
                            "search_type": {
                                "type": "string",
                                "enum": ["arxiv_papers", "github_repos", "research_code", "academic_datasets", "conference_papers", "huggingface_models"],
                                "description": "搜索类型：arxiv_papers(arXiv论文)、github_repos(GitHub代码库)、research_code(研究代码)、academic_datasets(学术数据集)、conference_papers(会议论文)、huggingface_models(Hugging Face模型)"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "最大结果数量，默认5",
                                "default": 5
                            }
                        },
                        "required": ["query", "search_type"]
                    }
                }
            }
        ]
    
    async def intelligent_search(
        self, 
        topic: str, 
        language: str = "zh",
        model: str = None
    ) -> SearchResults:
        """
        智能搜索，让大模型自主决定搜索策略
        
        Args:
            topic: 搜索主题
            language: 语言
            model: 指定的模型
            
        Returns:
            SearchResults: 聚合的搜索结果
        """
        start_time = datetime.now()
        self.logger.info(f"开始智能搜索: {topic}")
        
        try:
            # 第一步：让大模型分析主题并决定搜索策略
            search_plan = await self._generate_search_plan(topic, language, model)
            
            # 第二步：执行搜索计划
            all_results = []
            search_tasks = []
            
            for search_call in search_plan:
                task = self._execute_search_call(search_call)
                search_tasks.append(task)
            
            # 并行执行所有搜索任务
            search_results_list = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # 合并搜索结果
            for results in search_results_list:
                if isinstance(results, SearchResults):
                    all_results.extend(results.results)
                elif isinstance(results, Exception):
                    self.logger.warning(f"搜索任务失败: {results}")
                    continue
            
            # 去重和排序
            unique_results = self.search_service._deduplicate_results(all_results)
            sorted_results = self.search_service._sort_results_by_relevance(unique_results, topic)
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"智能搜索完成，找到 {len(sorted_results)} 个结果，耗时: {search_time:.2f}s")
            
            return SearchResults(
                query=topic,
                results=sorted_results,
                total_count=len(sorted_results),
                search_time=search_time,
                filters_applied={
                    "intelligent_search": True,
                    "search_calls": len(search_plan),
                    "model_used": model or self.settings.default_llm_model
                }
            )
            
        except Exception as e:
            self.logger.error(f"智能搜索失败: {e}", exc_info=True)
            raise SearchException(f"智能搜索失败: {str(e)}")
    
    async def _generate_search_plan(
        self, 
        topic: str, 
        language: str,
        model: str = None
    ) -> List[Dict[str, Any]]:
        """
        生成搜索计划，让大模型决定如何搜索
        """
        self.logger.info(f"让大模型分析主题并制定搜索策略: {topic}")
        
        # 构建提示词
        if language == "zh":
            prompt = f"""
你是一个智能搜索助手。用户想要了解关于"{topic}"的相关资源。

请分析这个主题，然后调用搜索工具来收集全面的信息。你应该：

1. 分析主题的不同方面和子领域
2. 为每个重要方面设计具体的搜索查询
3. 选择合适的搜索类型（通用、学术、代码、教程、工具）
4. 并行调用多个搜索以获得全面的结果

搜索类型说明：
- arxiv_papers: arXiv论文搜索，获取最新研究论文
- github_repos: GitHub代码库搜索，获取开源实现
- huggingface_models: Hugging Face模型搜索，获取预训练模型
- research_code: 研究代码搜索，获取论文配套代码
- academic_datasets: 学术数据集搜索，获取研究数据
- conference_papers: 会议论文搜索，获取顶级会议论文

请根据主题特点，调用3-5次搜索，覆盖学术研究的不同方面。
"""
        else:
            prompt = f"""
You are an intelligent search assistant. The user wants to learn about "{topic}".

Please analyze this topic and call search tools to gather comprehensive information. You should:

1. Analyze different aspects and subfields of the topic
2. Design specific search queries for each important aspect
3. Choose appropriate search types (general, academic, code, tutorial, tools)
4. Make parallel search calls to get comprehensive results

Search type descriptions:
- arxiv_papers: arXiv paper search for latest research papers
- github_repos: GitHub repository search for open source implementations
- huggingface_models: Hugging Face model search for pre-trained models
- research_code: Research code search for paper-associated code
- academic_datasets: Academic dataset search for research data
- conference_papers: Conference paper search for top-tier venue papers

Based on the topic characteristics, please make 3-5 search calls covering different aspects of academic research.
"""
        
        try:
            used_model = model or self.settings.default_llm_model
            
            response = await self.llm_service._call_llm(
                model=used_model,
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7,
                tools=self.search_tools,
                tool_choice="auto"
            )
            
            # 解析工具调用
            search_calls = self._parse_tool_calls(response)
            
            self.logger.info(f"大模型制定了 {len(search_calls)} 个搜索计划")
            return search_calls
            
        except Exception as e:
            self.logger.error(f"生成搜索计划失败: {e}")
            # 降级到默认搜索策略
            return self._get_fallback_search_plan(topic)
    
    def _parse_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """
        解析LLM的工具调用响应
        """
        try:
            # 尝试解析JSON格式的工具调用
            if response.startswith("{"):
                data = json.loads(response)
                if "tool_calls" in data:
                    search_calls = []
                    for tool_call in data["tool_calls"]:
                        if tool_call["function"]["name"] == "search_web":
                            args = json.loads(tool_call["function"]["arguments"])
                            search_calls.append(args)
                    return search_calls
            
            # 如果不是工具调用格式，返回空列表
            return []
            
        except Exception as e:
            self.logger.warning(f"解析工具调用失败: {e}")
            return []
    
    def _get_fallback_search_plan(self, topic: str) -> List[Dict[str, Any]]:
        """
        获取默认的学术搜索策略（降级方案）
        """
        self.logger.info("使用默认学术搜索策略")
        
        return [
            {
                "query": f"{topic} paper",
                "search_type": "arxiv_papers",
                "max_results": 4
            },
            {
                "query": f"{topic} implementation github",
                "search_type": "github_repos", 
                "max_results": 4
            },
            {
                "query": f"{topic} research code",
                "search_type": "research_code",
                "max_results": 2
            },
            {
                "query": f"{topic} huggingface",
                "search_type": "huggingface_models",
                "max_results": 2
            }
        ]
    
    async def _execute_search_call(self, search_call: Dict[str, Any]) -> SearchResults:
        """
        执行单个搜索调用
        """
        query = search_call.get("query", "")
        search_type = search_call.get("search_type", "general")
        max_results = search_call.get("max_results", 5)
        
        self.logger.debug(f"执行搜索: {query} (类型: {search_type})")
        
        try:
            # 根据学术搜索类型调整搜索参数
            include_domains = None
            exclude_domains = None
            
            if search_type == "arxiv_papers":
                include_domains = ["arxiv.org"]
                query += " paper research"
            elif search_type == "github_repos":
                include_domains = ["github.com"]
                query += " repository implementation"
            elif search_type == "research_code":
                include_domains = ["github.com"]
                query += " code implementation paper"
            elif search_type == "academic_datasets":
                include_domains = ["github.com", "arxiv.org"]
                query += " dataset data"
            elif search_type == "conference_papers":
                include_domains = ["arxiv.org"]
                query += " conference paper publication"
            elif search_type == "huggingface_models":
                include_domains = ["huggingface.co"]
                query += " model pre-trained"
            
            # 调用基础搜索服务（学术模式）
            results = await self.search_service.search_topic(
                topic=query,
                max_results=max_results,
                search_depth="basic",
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                academic_only=True
            )
            
            # 添加搜索类型标记
            for result in results.results:
                result.source = f"{result.source}_{search_type}"
            
            return results
            
        except Exception as e:
            self.logger.error(f"执行搜索调用失败: {e}")
            # 返回空结果而不是抛出异常
            return SearchResults(
                query=query,
                results=[],
                total_count=0,
                search_time=0,
                filters_applied={"error": str(e)}
            ) 