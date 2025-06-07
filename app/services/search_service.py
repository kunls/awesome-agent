"""
搜索服务模块
集成Tavily API实现多源智能搜索
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from tavily import TavilyClient
import httpx

from app.models import SearchResult, SearchResults, ExtendedTopic
from app.utils import get_settings, get_logger, SearchException, APIException, LoggerMixin


class SearchService(LoggerMixin):
    """
    搜索服务类
    负责集成Tavily API进行智能搜索
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.tavily_client = TavilyClient(api_key=self.settings.tavily_api_key)
        
    async def search_topic(
        self,
        topic: str,
        max_results: int = 10,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        academic_only: bool = True
    ) -> SearchResults:
        """
        搜索指定主题的相关资源
        
        Args:
            topic: 搜索主题
            max_results: 最大结果数量
            search_depth: 搜索深度 (basic/advanced)
            include_domains: 包含的域名列表
            exclude_domains: 排除的域名列表
            academic_only: 是否仅搜索学术资源 (arXiv, GitHub, Hugging Face)
            
        Returns:
            SearchResults: 搜索结果
        """
        start_time = datetime.now()
        self.logger.info(f"开始搜索主题: {topic}, 最大结果数: {max_results}, 学术模式: {academic_only}")
        
        try:
            # 设置学术领域的域名限制
            if academic_only and not include_domains:
                include_domains = ["arxiv.org", "github.com", "huggingface.co"]
                self.logger.info("启用学术模式，限制搜索域名: arXiv, GitHub, Hugging Face")
            
            # 扩展搜索查询
            extended_queries = await self._generate_search_queries(topic, academic_only=academic_only)
            
            # 执行多个搜索查询
            all_results = []
            for query in extended_queries[:3]:  # 限制查询数量避免过多API调用
                try:
                    results = await self._search_with_tavily(
                        query=query,
                        max_results=max(3, max_results // len(extended_queries)),
                        search_depth=search_depth,
                        include_domains=include_domains,
                        exclude_domains=exclude_domains
                    )
                    all_results.extend(results)
                    
                    # 避免API限制，添加短暂延迟
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    self.logger.warning(f"搜索查询 '{query}' 失败: {e}")
                    continue
            
            # 去重和排序
            unique_results = self._deduplicate_results(all_results)
            sorted_results = self._sort_results_by_relevance(unique_results, topic)
            
            # 限制结果数量
            final_results = sorted_results[:max_results]
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            self.logger.info(f"搜索完成，找到 {len(final_results)} 个结果，耗时: {search_time:.2f}s")
            
            return SearchResults(
                query=topic,
                results=final_results,
                total_count=len(final_results),
                search_time=search_time,
                filters_applied={
                    "max_results": max_results,
                    "search_depth": search_depth,
                    "include_domains": include_domains,
                    "exclude_domains": exclude_domains,
                    "academic_only": academic_only
                }
            )
            
        except Exception as e:
            self.logger.error(f"搜索过程中发生错误: {e}", exc_info=True)
            raise SearchException(f"搜索失败: {str(e)}")
    
    async def _generate_search_queries(self, topic: str, academic_only: bool = True) -> List[str]:
        """
        生成搜索查询列表
        基于主题生成多个相关的搜索查询，针对学术和科研领域优化
        """
        if academic_only:
            # 学术和科研领域的查询
            queries = [
                topic,
                f"{topic} paper",
                f"{topic} implementation", 
                f"{topic} github",
                f"{topic} arxiv",
                f"{topic} algorithm",
                f"{topic} code",
                f"{topic} research"
            ]
            
            # 针对不同学术领域优化查询
            if any(keyword in topic.lower() for keyword in ["deep learning", "机器学习", "neural network", "ai", "artificial intelligence"]):
                queries.extend([
                    f"{topic} model",
                    f"{topic} dataset",
                    f"{topic} benchmark",
                    f"{topic} pytorch",
                    f"{topic} tensorflow"
                ])
            elif any(keyword in topic.lower() for keyword in ["computer vision", "cv", "图像", "视觉"]):
                queries.extend([
                    f"{topic} opencv",
                    f"{topic} detection",
                    f"{topic} segmentation"
                ])
            elif any(keyword in topic.lower() for keyword in ["nlp", "自然语言", "language", "text"]):
                queries.extend([
                    f"{topic} transformer",
                    f"{topic} bert",
                    f"{topic} huggingface"
                ])
            elif any(keyword in topic.lower() for keyword in ["algorithm", "algorithms", "算法"]):
                queries.extend([
                    f"{topic} implementation",
                    f"{topic} complexity",
                    f"{topic} optimization"
                ])
        else:
            # 传统的通用查询
            queries = [
                topic,
                f"{topic} tutorial",
                f"{topic} documentation", 
                f"{topic} examples",
                f"awesome {topic}",
                f"{topic} tools"
            ]
        
        return queries
    
    async def _search_with_tavily(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """
        使用Tavily API执行搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            search_depth: 搜索深度
            include_domains: 包含的域名
            exclude_domains: 排除的域名
            
        Returns:
            List[SearchResult]: 搜索结果列表
        """
        try:
            self.logger.debug(f"执行Tavily搜索: {query}")
            
            # 构建搜索参数
            search_params = {
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_answer": False,  # 我们只需要搜索结果，不需要答案
                "include_raw_content": False,  # 不需要原始内容
            }
            
            if include_domains:
                search_params["include_domains"] = include_domains
            if exclude_domains:
                search_params["exclude_domains"] = exclude_domains
            
            # 执行搜索
            response = self.tavily_client.search(**search_params)
            
            # 解析结果
            results = []
            for item in response.get("results", []):
                try:
                    result = SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        content=item.get("content", ""),
                        score=float(item.get("score", 0.0)),
                        source=self._determine_source_type(item.get("url", "")),
                        published_date=item.get("published_date")
                    )
                    results.append(result)
                except Exception as e:
                    self.logger.warning(f"解析搜索结果项失败: {e}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"Tavily搜索失败: {e}")
            raise APIException(f"Tavily搜索API调用失败: {str(e)}")
    
    def _determine_source_type(self, url: str) -> str:
        """
        根据URL确定内容源类型
        """
        url_lower = url.lower()
        
        if "github.com" in url_lower:
            return "github"
        elif "stackoverflow.com" in url_lower:
            return "stackoverflow"
        elif "arxiv.org" in url_lower:
            return "arxiv"
        elif any(domain in url_lower for domain in ["docs.", "documentation"]):
            return "documentation"
        elif any(domain in url_lower for domain in ["blog", "medium.com", "dev.to"]):
            return "blog"
        elif any(domain in url_lower for domain in ["youtube.com", "youtu.be"]):
            return "video"
        elif any(domain in url_lower for domain in ["reddit.com", "news.ycombinator.com"]):
            return "forum"
        else:
            return "website"
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        去除重复的搜索结果
        """
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        return unique_results
    
    def _sort_results_by_relevance(
        self, 
        results: List[SearchResult], 
        topic: str
    ) -> List[SearchResult]:
        """
        按相关性对搜索结果排序
        """
        def calculate_relevance_score(result: SearchResult) -> float:
            score = result.score
            
            # 根据源类型调整分数
            source_weights = {
                "github": 1.2,
                "documentation": 1.3,
                "arxiv": 1.1,
                "stackoverflow": 1.0,
                "blog": 0.9,
                "video": 0.8,
                "forum": 0.7,
                "website": 0.8
            }
            score *= source_weights.get(result.source, 1.0)
            
            # 根据标题和内容中的关键词匹配调整分数
            topic_keywords = topic.lower().split()
            title_lower = result.title.lower()
            content_lower = result.content.lower()
            
            keyword_bonus = 0
            for keyword in topic_keywords:
                if keyword in title_lower:
                    keyword_bonus += 0.1
                if keyword in content_lower:
                    keyword_bonus += 0.05
            
            score += keyword_bonus
            
            return score
        
        # 按相关性分数排序
        return sorted(
            results, 
            key=calculate_relevance_score, 
            reverse=True
        ) 