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
        
        # 显示使用的模型
        used_model = model or self.settings.default_llm_model
        self.logger.info(f"🤖 使用模型: {used_model}")
        
        # 构建提示词
        if language == "zh":
            prompt = f"""
你是一个智能搜索助手。用户想要了解关于"{topic}"的相关资源。

**重要：你必须使用search_web工具来搜索信息，不要只给文字回答。**

请按以下步骤操作：
1. 分析"{topic}"主题的不同方面
2. 立即调用search_web工具进行搜索
3. 至少调用3-4次搜索，覆盖不同角度

可用的搜索类型：
- arxiv_papers: 搜索arXiv学术论文
- github_repos: 搜索GitHub代码库
- huggingface_models: 搜索Hugging Face模型
- research_code: 搜索研究代码
- academic_datasets: 搜索学术数据集

现在请立即开始搜索：
"""
        else:
            prompt = f"""
You are an intelligent search assistant. The user wants to learn about "{topic}".

**IMPORTANT: You MUST use the search_web tool to search for information. Do not just provide text responses.**

Please follow these steps:
1. Analyze the different aspects of "{topic}"
2. Immediately call the search_web tool to search
3. Make at least 3-4 search calls covering different angles

Available search types:
- arxiv_papers: Search arXiv academic papers
- github_repos: Search GitHub repositories
- huggingface_models: Search Hugging Face models
- research_code: Search research code
- academic_datasets: Search academic datasets

Now please start searching immediately:
"""
        
        try:
            response = await self.llm_service._call_llm(
                model=used_model,
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7,
                tools=self.search_tools,
                tool_choice="auto"
            )
            
            self.logger.info(f"LLM完整响应: {response}")
            
            # 解析工具调用
            search_calls = self._parse_tool_calls(response)
            
            self.logger.info(f"大模型制定了 {len(search_calls)} 个搜索计划")
            
            # 如果没有工具调用，记录详细信息
            if len(search_calls) == 0:
                self.logger.warning(f"大模型没有调用搜索工具，响应内容: {response[:500]}")
                self.logger.info("将使用降级搜索策略")
                return self._get_fallback_search_plan(topic)
            
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
            self.logger.debug(f"解析工具调用响应: {response}")
            
            # 尝试解析JSON格式的工具调用
            if response.strip().startswith("{"):
                data = json.loads(response)
                if "tool_calls" in data:
                    search_calls = []
                    for tool_call in data["tool_calls"]:
                        if tool_call.get("function", {}).get("name") == "search_web":
                            args_str = tool_call["function"]["arguments"]
                            # 参数可能已经是字符串形式
                            if isinstance(args_str, str):
                                args = json.loads(args_str)
                            else:
                                args = args_str
                            search_calls.append(args)
                    return search_calls
            
            # 尝试查找文本中的工具调用模式
            # 有时LLM可能会生成自然语言描述而不是严格的JSON
            import re
            
            # 寻找search_web调用的模式
            patterns = [
                r'search_web\s*\(\s*query["\']?\s*:\s*["\']([^"\']+)["\']',
                r'query["\']?\s*:\s*["\']([^"\']+)["\']',
                r'搜索[：:]\s*["\']?([^"\']+)["\']?'
            ]
            
            search_calls = []
            for pattern in patterns:
                matches = re.findall(pattern, response, re.IGNORECASE)
                for match in matches:
                    search_calls.append({
                        "query": match.strip(),
                        "search_type": "arxiv_papers",  # 默认类型
                        "max_results": 3
                    })
            
            if search_calls:
                self.logger.info(f"通过正则表达式解析出 {len(search_calls)} 个搜索调用")
                return search_calls[:5]  # 限制数量
            
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
        # 正确获取查询参数：从arguments中获取
        arguments = search_call.get("arguments", {})
        query = arguments.get("query", "")
        search_type = arguments.get("search_type", "general")
        max_results = arguments.get("max_results", 5)
        
        # 验证查询不为空
        if not query or not query.strip():
            self.logger.warning(f"⚠️ 搜索查询为空，跳过执行: {search_call}")
            return SearchResults(
                query="",
                results=[],
                total_count=0,
                search_time=0,
                filters_applied={"error": "Empty query"}
            )
        
        clean_query = query.strip()
        self.logger.debug(f"执行搜索: {clean_query} (类型: {search_type})")
        
        try:
            # 根据学术搜索类型调整搜索参数
            include_domains = None
            exclude_domains = None
            
            if search_type == "arxiv_papers":
                include_domains = ["arxiv.org"]
                clean_query += " paper research"
            elif search_type == "github_repos":
                include_domains = ["github.com"]
                clean_query += " repository implementation"
            elif search_type == "research_code":
                include_domains = ["github.com"]
                clean_query += " code implementation paper"
            elif search_type == "academic_datasets":
                include_domains = ["github.com", "arxiv.org"]
                clean_query += " dataset data"
            elif search_type == "conference_papers":
                include_domains = ["arxiv.org"]
                clean_query += " conference paper publication"
            elif search_type == "huggingface_models":
                include_domains = ["huggingface.co"]
                clean_query += " model pre-trained"
            
            # 调用基础搜索服务（学术模式）
            results = await self.search_service.search_topic(
                topic=clean_query,
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
                query=clean_query,
                results=[],
                total_count=0,
                search_time=0,
                filters_applied={"error": str(e)}
            )

    async def intelligent_search_with_topics(
        self,
        original_topic: str,
        extended_topic,  # ExtendedTopic对象
        language: str = "zh",
        model: str = None,
        max_results: int = 20
    ) -> SearchResults:
        """
        根据扩展主题进行智能搜索
        
        Args:
            original_topic: 原始主题
            extended_topic: 扩展主题对象
            language: 语言
            model: 指定的模型
            max_results: 最大结果数
            
        Returns:
            SearchResults: 聚合的搜索结果
        """
        start_time = datetime.now()
        self.logger.info(f"🔍 开始基于扩展主题的智能搜索")
        
        try:
            # 构建搜索计划：使用扩展的关键词和相关概念
            search_plan = self._generate_search_plan_from_topics(
                original_topic, 
                extended_topic, 
                language, 
                model
            )
            
            # 执行搜索计划
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
                    self.logger.warning(f"⚠️ 搜索任务失败: {results}")
                    continue
            
            # 去重和排序
            unique_results = self.search_service._deduplicate_results(all_results)
            sorted_results = self.search_service._sort_results_by_relevance(unique_results, original_topic)
            
            # 限制结果数量
            final_results = sorted_results[:max_results]
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"🎉 基于扩展主题的智能搜索完成，找到 {len(final_results)} 个结果，耗时: {search_time:.2f}s")
            
            return SearchResults(
                query=original_topic,
                results=final_results,
                total_count=len(final_results),
                search_time=search_time,
                filters_applied={
                    "intelligent_search_with_topics": True,
                    "search_calls": len(search_plan),
                    "model_used": model or self.settings.default_llm_model,
                    "extended_keywords": len(extended_topic.extended_keywords),
                    "related_concepts": len(extended_topic.related_concepts)
                }
            )
            
        except Exception as e:
            self.logger.error(f"❌ 基于扩展主题的智能搜索失败: {e}", exc_info=True)
            raise SearchException(f"智能搜索失败: {str(e)}")

    def _generate_search_plan_from_topics(
        self, 
        original_topic: str,
        extended_topic,  # ExtendedTopic对象
        language: str,
        model: str = None
    ) -> List[Dict[str, Any]]:
        """
        基于扩展主题生成搜索计划
        """
        self.logger.info(f"📝 基于扩展主题制定搜索计划")
        self.logger.info(f"🔑 扩展关键词: {extended_topic.extended_keywords}")
        self.logger.info(f"💡 相关概念: {extended_topic.related_concepts}")
        
        search_calls = []
        
        # 为每个扩展关键词和相关概念创建搜索调用
        all_search_terms = []
        
        # 过滤掉空字符串和None值
        valid_keywords = [kw.strip() for kw in extended_topic.extended_keywords if kw and kw.strip()]
        valid_concepts = [concept.strip() for concept in extended_topic.related_concepts if concept and concept.strip()]
        
        self.logger.info(f"✅ 有效关键词: {valid_keywords}")
        self.logger.info(f"✅ 有效概念: {valid_concepts}")
        
        all_search_terms.extend(valid_keywords[:3])  # 最多3个关键词
        all_search_terms.extend(valid_concepts[:2])   # 最多2个概念
        
        # 如果没有有效的搜索词，使用原始主题
        if not all_search_terms:
            self.logger.warning(f"⚠️ 没有有效的扩展搜索词，使用原始主题: {original_topic}")
            all_search_terms = [original_topic]
        
        # 为每个搜索词创建不同类型的搜索
        search_types = ["arxiv_papers", "github_repos", "huggingface_models", "academic_datasets"]
        
        for i, search_term in enumerate(all_search_terms):
            # 确保搜索词不为空
            if not search_term or not search_term.strip():
                self.logger.warning(f"⚠️ 跳过空搜索词: '{search_term}'")
                continue
                
            clean_search_term = search_term.strip()
            self.logger.debug(f"🔍 为搜索词 '{clean_search_term}' 创建搜索计划")
            
            # 每个搜索词使用2种搜索类型
            for j, search_type in enumerate(search_types[:2]):
                search_calls.append({
                    "function": "search_web",
                    "arguments": {
                        "query": clean_search_term,
                        "search_type": search_type,
                        "max_results": 3
                    }
                })
                
                # 限制总搜索次数
                if len(search_calls) >= 8:
                    break
            
            if len(search_calls) >= 8:
                break
        
        self.logger.info(f"📊 制定了 {len(search_calls)} 个搜索计划")
        
        # 确保至少有一个搜索计划
        if not search_calls:
            self.logger.warning(f"⚠️ 没有生成搜索计划，使用原始主题: {original_topic}")
            search_calls = [{
                "function": "search_web",
                "arguments": {
                    "query": original_topic,
                    "search_type": "arxiv_papers",
                    "max_results": 5
                }
            }]
        
        return search_calls 