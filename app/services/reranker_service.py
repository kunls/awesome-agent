"""
Reranker RAG 服务
基于学术权威性、相关性和时效性对搜索结果进行重新排序
支持规则评分和大模型评分两种模式
"""

import asyncio
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Literal
from dataclasses import dataclass
import aiohttp
import json

from app.models.search_models import SearchResult, SearchResults
from app.utils.logger import LoggerMixin
from app.services.llm_service import LLMService


@dataclass
class RerankingScore:
    """重排序得分详情"""
    total_score: float
    relevance_score: float
    authority_score: float
    recency_score: float
    completeness_score: float
    details: Dict[str, Any]


@dataclass
class LLMRerankingScore:
    """大模型重排序得分详情"""
    total_score: float
    relevance_score: float
    authority_score: float
    quality_score: float
    utility_score: float
    reasoning: str
    details: Dict[str, Any]


@dataclass
class ArxivMetadata:
    """arXiv论文元数据"""
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published_date: datetime
    updated_date: datetime
    comment: Optional[str] = None
    journal_ref: Optional[str] = None


@dataclass
class GitHubMetadata:
    """GitHub仓库元数据"""
    full_name: str
    description: str
    stars: int
    forks: int
    language: str
    created_at: datetime
    updated_at: datetime
    topics: List[str]
    has_issues: bool
    has_wiki: bool
    has_pages: bool
    size: int


class RerankerService(LoggerMixin):
    """
    Reranker RAG 服务
    对搜索结果进行学术导向的重新排序
    支持规则评分和大模型评分两种模式
    """
    
    def __init__(self):
        super().__init__()
        self.session: Optional[aiohttp.ClientSession] = None
        self.llm_service = LLMService()
        
        # 权重配置（规则评分）
        self.weights = {
            "relevance": 0.35,      # 相关性权重
            "authority": 0.30,      # 权威性权重  
            "recency": 0.20,        # 时效性权重
            "completeness": 0.15    # 完整性权重
        }
        
        # 大模型评分权重配置
        self.llm_weights = {
            "relevance": 0.30,      # 相关性权重
            "authority": 0.25,      # 权威性权重
            "quality": 0.25,        # 质量权重
            "utility": 0.20         # 实用性权重
        }
        
        # API配置
        self.github_api_base = "https://api.github.com"
        self.arxiv_api_base = "http://export.arxiv.org/api/query"
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "User-Agent": "AwesomeAgent/1.0 (Academic Research Tool)"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def rerank_search_results(
        self,
        search_results: SearchResults,
        query: str,
        target_count: Optional[int] = None,
        scoring_method: Literal["rule_based", "llm_based"] = "rule_based"
    ) -> SearchResults:
        """
        对搜索结果进行重新排序
        
        Args:
            search_results: 搜索结果
            query: 查询词
            target_count: 目标结果数量
            scoring_method: 评分方法 ("rule_based" 或 "llm_based")
        """
        start_time = datetime.now()
        self.logger.info(f"开始重排序 {len(search_results.results)} 个搜索结果，查询: {query}，评分方法: {scoring_method}")
        
        try:
            async with self:
                # 根据评分方法选择处理流程
                if scoring_method == "llm_based":
                    scores = await self._calculate_llm_scores_batch(search_results.results, query)
                else:
                    # 并行计算规则评分
                    tasks = [
                        self._calculate_reranking_score(result, query)
                        for result in search_results.results
                    ]
                    scores = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 处理结果
                valid_results = []
                for i, score in enumerate(scores):
                    if isinstance(score, Exception):
                        self.logger.warning(f"重排序第{i}个结果失败: {score}")
                        # 根据评分方法使用相应的默认评分结构
                        if scoring_method == "llm_based":
                            score = LLMRerankingScore(
                                total_score=search_results.results[i].score,
                                relevance_score=search_results.results[i].score,
                                authority_score=0.0,
                                quality_score=0.0,
                                utility_score=0.0,
                                reasoning="评分失败，使用原始分数",
                                details={"error": str(score)}
                            )
                        else:
                            score = RerankingScore(
                                total_score=search_results.results[i].score,
                                relevance_score=search_results.results[i].score,
                                authority_score=0.0,
                                recency_score=0.0,
                                completeness_score=0.0,
                                details={"error": str(score)}
                            )
                    valid_results.append((search_results.results[i], score))
                
                # 按总分排序
                valid_results.sort(key=lambda x: x[1].total_score, reverse=True)
                
                # 限制结果数量
                if target_count:
                    valid_results = valid_results[:target_count]
                
                # 构建重排序结果
                reranked_results = []
                for result, score in valid_results:
                    reranked_result = SearchResult(
                        title=result.title,
                        url=result.url,
                        content=result.content,
                        score=score.total_score,
                        source=result.source,
                        published_date=result.published_date
                    )
                    reranked_results.append(reranked_result)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                self.logger.info(
                    f"重排序完成，处理 {len(reranked_results)} 个结果，"
                    f"耗时: {processing_time:.2f}秒"
                )
                
                # 根据评分方法设置不同的过滤器信息
                filters_applied = {
                    **search_results.filters_applied,
                    "reranked": True,
                    "scoring_method": scoring_method
                }
                
                if scoring_method == "llm_based":
                    filters_applied["reranking_weights"] = self.llm_weights
                else:
                    filters_applied["reranking_weights"] = self.weights
                
                return SearchResults(
                    query=search_results.query,
                    results=reranked_results,
                    total_count=len(reranked_results),
                    search_time=search_results.search_time + processing_time,
                    filters_applied=filters_applied
                )
                
        except Exception as e:
            self.logger.error(f"重排序过程中发生错误: {e}", exc_info=True)
            return search_results
    
    async def _calculate_reranking_score(
        self,
        result: SearchResult,
        query: str
    ) -> RerankingScore:
        """计算重排序得分"""
        try:
            # 根据来源获取元数据并计算得分
            url_str = str(result.url)
            if "arxiv.org" in url_str:
                metadata = await self._get_arxiv_metadata(url_str)
                scores = await self._calculate_arxiv_scores(metadata, result, query)
            elif "github.com" in url_str:
                metadata = await self._get_github_metadata(url_str)
                scores = await self._calculate_github_scores(metadata, result, query)
            else:
                scores = await self._calculate_basic_scores(result, query)
            
            # 计算加权总分
            total_score = (
                scores["relevance"] * self.weights["relevance"] +
                scores["authority"] * self.weights["authority"] +
                scores["recency"] * self.weights["recency"] +
                scores["completeness"] * self.weights["completeness"]
            )
            
            return RerankingScore(
                total_score=total_score,
                relevance_score=scores["relevance"],
                authority_score=scores["authority"],
                recency_score=scores["recency"],
                completeness_score=scores["completeness"],
                details=scores.get("details", {})
            )
            
        except Exception as e:
            self.logger.warning(f"计算重排序得分失败 {result.url}: {e}")
            return RerankingScore(
                total_score=result.score,
                relevance_score=result.score,
                authority_score=0.0,
                recency_score=0.0,
                completeness_score=0.0,
                details={"error": str(e)}
            )
    
    async def _get_arxiv_metadata(self, arxiv_url: str) -> Optional[ArxivMetadata]:
        """获取arXiv论文元数据"""
        try:
            arxiv_id = self._extract_arxiv_id(arxiv_url)
            if not arxiv_id:
                return None
            
            api_url = f"{self.arxiv_api_base}?id_list={arxiv_id}"
            
            async with self.session.get(api_url) as response:
                if response.status != 200:
                    self.logger.warning(f"arXiv API请求失败: {response.status}")
                    return None
                
                xml_content = await response.text()
                return self._parse_arxiv_response(xml_content)
                
        except Exception as e:
            self.logger.warning(f"获取arXiv元数据失败 {arxiv_url}: {e}")
            return None
    
    async def _get_github_metadata(self, github_url: str) -> Optional[GitHubMetadata]:
        """获取GitHub仓库元数据"""
        try:
            repo_path = self._extract_github_repo(github_url)
            if not repo_path:
                return None
            
            api_url = f"{self.github_api_base}/repos/{repo_path}"
            
            async with self.session.get(api_url) as response:
                if response.status != 200:
                    self.logger.warning(f"GitHub API请求失败: {response.status}")
                    return None
                
                repo_data = await response.json()
                return self._parse_github_response(repo_data)
                
        except Exception as e:
            self.logger.warning(f"获取GitHub元数据失败 {github_url}: {e}")
            return None
    
    def _extract_arxiv_id(self, url: str) -> Optional[str]:
        """从arXiv URL中提取论文ID"""
        patterns = [
            r"arxiv\.org/abs/([^/?]+)",
            r"arxiv\.org/pdf/([^/?]+)",
            r"export\.arxiv\.org/abs/([^/?]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _extract_github_repo(self, url: str) -> Optional[str]:
        """从GitHub URL中提取owner/repo"""
        pattern = r"github\.com/([^/]+/[^/?]+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None
    
    def _parse_arxiv_response(self, xml_content: str) -> Optional[ArxivMetadata]:
        """解析arXiv API响应"""
        try:
            root = ET.fromstring(xml_content)
            
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            entry = root.find('atom:entry', ns)
            if entry is None:
                return None
            
            title = entry.find('atom:title', ns).text.strip()
            published = datetime.fromisoformat(
                entry.find('atom:published', ns).text.replace('Z', '+00:00')
            )
            updated = datetime.fromisoformat(
                entry.find('atom:updated', ns).text.replace('Z', '+00:00')
            )
            summary = entry.find('atom:summary', ns).text.strip()
            
            # 提取作者
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns)
                if name is not None:
                    authors.append(name.text)
            
            # 提取分类
            categories = []
            for category in entry.findall('atom:category', ns):
                term = category.get('term')
                if term:
                    categories.append(term)
            
            arxiv_id = entry.find('atom:id', ns).text.split('/')[-1]
            
            # 可选字段
            comment_elem = entry.find('arxiv:comment', ns)
            comment = comment_elem.text if comment_elem is not None else None
            
            journal_elem = entry.find('arxiv:journal_ref', ns)
            journal_ref = journal_elem.text if journal_elem is not None else None
            
            return ArxivMetadata(
                arxiv_id=arxiv_id,
                title=title,
                authors=authors,
                abstract=summary,
                categories=categories,
                published_date=published,
                updated_date=updated,
                comment=comment,
                journal_ref=journal_ref
            )
            
        except Exception as e:
            self.logger.warning(f"解析arXiv响应失败: {e}")
            return None
    
    def _parse_github_response(self, repo_data: Dict[str, Any]) -> GitHubMetadata:
        """解析GitHub API响应"""
        return GitHubMetadata(
            full_name=repo_data.get('full_name', ''),
            description=repo_data.get('description', '') or '',
            stars=repo_data.get('stargazers_count', 0),
            forks=repo_data.get('forks_count', 0),
            language=repo_data.get('language', '') or '',
            created_at=datetime.fromisoformat(
                repo_data.get('created_at', '').replace('Z', '+00:00')
            ),
            updated_at=datetime.fromisoformat(
                repo_data.get('updated_at', '').replace('Z', '+00:00')
            ),
            topics=repo_data.get('topics', []),
            has_issues=repo_data.get('has_issues', False),
            has_wiki=repo_data.get('has_wiki', False),
            has_pages=repo_data.get('has_pages', False),
            size=repo_data.get('size', 0)
        )
    
    async def _calculate_arxiv_scores(
        self,
        metadata: Optional[ArxivMetadata],
        result: SearchResult,
        query: str
    ) -> Dict[str, Any]:
        """计算arXiv论文得分"""
        if not metadata:
            return await self._calculate_basic_scores(result, query)
        
        relevance_score = self._calculate_text_relevance(
            query, 
            f"{metadata.title} {metadata.abstract}",
            result.score
        )
        
        authority_score = self._calculate_arxiv_authority(metadata)
        recency_score = self._calculate_recency_score(metadata.published_date)
        completeness_score = self._calculate_arxiv_completeness(metadata)
        
        return {
            "relevance": relevance_score,
            "authority": authority_score,
            "recency": recency_score,
            "completeness": completeness_score,
            "details": {
                "source": "arxiv",
                "arxiv_id": metadata.arxiv_id,
                "categories": metadata.categories,
                "authors_count": len(metadata.authors),
                "has_journal_ref": bool(metadata.journal_ref)
            }
        }
    
    async def _calculate_github_scores(
        self,
        metadata: Optional[GitHubMetadata],
        result: SearchResult,
        query: str
    ) -> Dict[str, Any]:
        """计算GitHub仓库得分"""
        if not metadata:
            return await self._calculate_basic_scores(result, query)
        
        relevance_score = self._calculate_text_relevance(
            query,
            f"{metadata.full_name} {metadata.description} {' '.join(metadata.topics)}",
            result.score
        )
        
        authority_score = self._calculate_github_authority(metadata)
        recency_score = self._calculate_recency_score(metadata.updated_at)
        completeness_score = self._calculate_github_completeness(metadata)
        
        return {
            "relevance": relevance_score,
            "authority": authority_score,
            "recency": recency_score,
            "completeness": completeness_score,
            "details": {
                "source": "github",
                "stars": metadata.stars,
                "forks": metadata.forks,
                "language": metadata.language,
                "topics": metadata.topics
            }
        }
    
    async def _calculate_basic_scores(
        self,
        result: SearchResult,
        query: str
    ) -> Dict[str, Any]:
        """计算基础得分"""
        relevance_score = self._calculate_text_relevance(
            query,
            f"{result.title} {result.content}",
            result.score
        )
        
        return {
            "relevance": relevance_score,
            "authority": 0.5,
            "recency": 0.5,
            "completeness": 0.5,
            "details": {"source": "basic"}
        }
    
    def _calculate_text_relevance(self, query: str, text: str, original_score: float) -> float:
        """计算文本相关性"""
        try:
            query_lower = query.lower()
            text_lower = text.lower()
            
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in text_lower)
            word_match_score = matches / len(query_words) if query_words else 0
            
            exact_match_bonus = 0.2 if query_lower in text_lower else 0
            combined_score = word_match_score * 0.6 + original_score * 0.4 + exact_match_bonus
            
            return min(1.0, max(0.0, combined_score))
            
        except Exception:
            return original_score
    
    def _calculate_arxiv_authority(self, metadata: ArxivMetadata) -> float:
        """计算arXiv权威性得分"""
        score = 0.0
        
        # 高影响力分类
        high_impact_cats = ['cs.AI', 'cs.LG', 'cs.CV', 'cs.CL', 'stat.ML']
        if any(cat in high_impact_cats for cat in metadata.categories):
            score += 0.3
        
        # 作者数量
        author_count = len(metadata.authors)
        if 2 <= author_count <= 6:
            score += 0.2
        elif author_count > 6:
            score += 0.1
        
        # 期刊引用
        if metadata.journal_ref:
            score += 0.3
        
        # 更新次数
        if metadata.updated_date > metadata.published_date:
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_github_authority(self, metadata: GitHubMetadata) -> float:
        """计算GitHub权威性得分"""
        import math
        score = 0.0
        
        # Stars得分
        if metadata.stars > 0:
            stars_score = min(0.5, math.log10(metadata.stars + 1) / 4)
            score += stars_score
        
        # Forks得分
        if metadata.forks > 0:
            forks_score = min(0.2, math.log10(metadata.forks + 1) / 5)
            score += forks_score
        
        # 流行语言
        popular_langs = ['Python', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++']
        if metadata.language in popular_langs:
            score += 0.1
        
        # 项目特性
        if metadata.has_wiki:
            score += 0.05
        if metadata.has_issues:
            score += 0.05
        if metadata.topics:
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_recency_score(self, date: datetime) -> float:
        """计算时效性得分"""
        try:
            now = datetime.now(timezone.utc)
            days_old = (now - date.replace(tzinfo=timezone.utc)).days
            
            if days_old <= 30:
                return 1.0
            elif days_old <= 90:
                return 0.9
            elif days_old <= 365:
                return 0.7
            elif days_old <= 730:
                return 0.5
            elif days_old <= 1825:
                return 0.3
            else:
                return 0.1
                
        except Exception:
            return 0.5
    
    def _calculate_arxiv_completeness(self, metadata: ArxivMetadata) -> float:
        """计算arXiv完整性得分"""
        score = 0.0
        
        # 摘要长度
        if len(metadata.abstract) > 500:
            score += 0.3
        elif len(metadata.abstract) > 200:
            score += 0.2
        
        # 标题长度
        title_len = len(metadata.title)
        if 50 <= title_len <= 150:
            score += 0.2
        elif 30 <= title_len <= 200:
            score += 0.1
        
        # 分类数量
        if len(metadata.categories) >= 2:
            score += 0.2
        elif len(metadata.categories) == 1:
            score += 0.1
        
        # 注释和期刊引用
        if metadata.comment:
            score += 0.15
        if metadata.journal_ref:
            score += 0.15
        
        return min(1.0, score)
    
    def _calculate_github_completeness(self, metadata: GitHubMetadata) -> float:
        """计算GitHub完整性得分"""
        score = 0.0
        
        # 描述
        if metadata.description and len(metadata.description) > 50:
            score += 0.3
        elif metadata.description:
            score += 0.15
        
        # Topics
        topic_count = len(metadata.topics)
        if topic_count >= 3:
            score += 0.25
        elif topic_count >= 1:
            score += 0.15
        
        # 项目大小
        if 100 <= metadata.size <= 100000:
            score += 0.2
        
        # 活跃度
        recency = self._calculate_recency_score(metadata.updated_at)
        if recency > 0.7:
            score += 0.15
        
        # 特性
        if metadata.has_wiki:
            score += 0.05
        if metadata.has_pages:
            score += 0.05
        
        return min(1.0, score)

    async def _calculate_llm_scores_batch(
        self,
        results: List[SearchResult],
        query: str
    ) -> List[LLMRerankingScore]:
        """
        批量使用大模型对搜索结果进行评分
        
        Args:
            results: 搜索结果列表
            query: 原始查询词
            
        Returns:
            List[LLMRerankingScore]: 大模型评分结果列表
        """
        self.logger.info(f"开始使用大模型评分 {len(results)} 个搜索结果")
        
        try:
            # 将结果分批处理，避免单次请求过大
            batch_size = 5  # 每批最多5个结果
            all_scores = []
            
            for i in range(0, len(results), batch_size):
                batch = results[i:i + batch_size]
                self.logger.info(f"处理第 {i//batch_size + 1} 批，包含 {len(batch)} 个结果")
                
                batch_scores = await self._score_results_batch_with_llm(batch, query)
                all_scores.extend(batch_scores)
                
                # 避免API请求过于频繁
                if i + batch_size < len(results):
                    await asyncio.sleep(1)
            
            return all_scores
            
        except Exception as e:
            self.logger.error(f"大模型批量评分失败: {e}")
            # 返回默认评分
            return [
                LLMRerankingScore(
                    total_score=result.score,
                    relevance_score=result.score,
                    authority_score=0.5,
                    quality_score=0.5,
                    utility_score=0.5,
                    reasoning="LLM评分失败，使用默认分数",
                    details={"error": str(e)}
                )
                for result in results
            ]
    
    async def _score_results_batch_with_llm(
        self,
        results: List[SearchResult],
        query: str
    ) -> List[LLMRerankingScore]:
        """
        使用大模型对一批搜索结果进行评分
        """
        try:
            prompt = self._build_llm_scoring_prompt(results, query)
            
            # 调用大模型进行评分
            response = await self.llm_service._call_llm(
                model="gpt-4o-mini",  # 使用较快的模型进行评分
                prompt=prompt,
                max_tokens=2000,
                temperature=0.1  # 低温度确保评分一致性
            )
            
            # 解析响应
            scores = self._parse_llm_scoring_response(response, results)
            
            return scores
            
        except Exception as e:
            self.logger.error(f"LLM评分失败: {e}")
            # 返回默认评分
            return [
                LLMRerankingScore(
                    total_score=result.score,
                    relevance_score=result.score,
                    authority_score=0.5,
                    quality_score=0.5,
                    utility_score=0.5,
                    reasoning=f"LLM评分失败: {str(e)}",
                    details={"error": str(e)}
                )
                for result in results
            ]
    
    def _build_llm_scoring_prompt(
        self,
        results: List[SearchResult],
        query: str
    ) -> str:
        """
        构建大模型评分的提示词
        """
        # 构建结果信息
        results_info = []
        for i, result in enumerate(results, 1):
            result_text = f"""
结果 {i}:
标题: {result.title}
来源: {result.source}
链接: {result.url}
内容摘要: {result.content[:500]}...
发布时间: {result.published_date or '未知'}
原始评分: {result.score:.2f}
"""
            results_info.append(result_text)
        
        prompt = f"""
你是一个专业的学术搜索结果评分专家。请为以下搜索结果进行多维度评分。

查询词: "{query}"

搜索结果:
{"".join(results_info)}

请从以下4个维度对每个结果进行评分（0-1分）：

1. **相关性 (Relevance)**: 结果与查询词的匹配程度
   - 标题和内容是否直接回答查询
   - 关键词匹配度
   - 语义相关性

2. **权威性 (Authority)**: 来源的可信度和专业性
   - 来源类型（官方文档、GitHub热门项目、学术论文等）
   - 作者或机构声誉
   - 社区认可度

3. **质量 (Quality)**: 内容的质量和完整性
   - 信息的准确性和详细程度
   - 结构化程度
   - 可理解性

4. **实用性 (Utility)**: 对用户的实际价值
   - 可操作性
   - 实际应用价值
   - 学习或参考价值

请严格按照以下JSON格式返回评分结果，不要添加任何其他内容：

{{
  "scores": [
    {{
      "result_index": 1,
      "relevance_score": 0.85,
      "authority_score": 0.90,
      "quality_score": 0.80,
      "utility_score": 0.88,
      "reasoning": "详细说明评分理由"
    }},
    {{
      "result_index": 2,
      "relevance_score": 0.75,
      "authority_score": 0.70,
      "quality_score": 0.85,
      "utility_score": 0.80,
      "reasoning": "详细说明评分理由"
    }}
  ]
}}

评分标准：
- 0.9-1.0: 优秀
- 0.8-0.9: 良好  
- 0.7-0.8: 一般
- 0.6-0.7: 较差
- 0.0-0.6: 很差
"""
        
        return prompt
    
    def _parse_llm_scoring_response(
        self,
        response: str,
        results: List[SearchResult]
    ) -> List[LLMRerankingScore]:
        """
        解析大模型评分响应
        """
        try:
            # 尝试解析JSON响应
            import json
            
            # 提取JSON部分
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            
            parsed_response = json.loads(response)
            scores_data = parsed_response.get("scores", [])
            
            # 构建评分结果
            llm_scores = []
            
            for i, result in enumerate(results):
                # 查找对应的评分数据
                score_data = None
                for score in scores_data:
                    if score.get("result_index") == i + 1:
                        score_data = score
                        break
                
                if score_data:
                    # 计算加权总分
                    total_score = (
                        score_data.get("relevance_score", 0.5) * self.llm_weights["relevance"] +
                        score_data.get("authority_score", 0.5) * self.llm_weights["authority"] +
                        score_data.get("quality_score", 0.5) * self.llm_weights["quality"] +
                        score_data.get("utility_score", 0.5) * self.llm_weights["utility"]
                    )
                    
                    llm_score = LLMRerankingScore(
                        total_score=total_score,
                        relevance_score=score_data.get("relevance_score", 0.5),
                        authority_score=score_data.get("authority_score", 0.5),
                        quality_score=score_data.get("quality_score", 0.5),
                        utility_score=score_data.get("utility_score", 0.5),
                        reasoning=score_data.get("reasoning", "无详细说明"),
                        details={
                            "llm_model": "gpt-4o-mini",
                            "weights_used": self.llm_weights
                        }
                    )
                else:
                    # 使用默认评分
                    llm_score = LLMRerankingScore(
                        total_score=result.score,
                        relevance_score=result.score,
                        authority_score=0.5,
                        quality_score=0.5,
                        utility_score=0.5,
                        reasoning="LLM响应中未找到对应评分",
                        details={"error": "missing_score_data"}
                    )
                
                llm_scores.append(llm_score)
            
            return llm_scores
            
        except json.JSONDecodeError as e:
            self.logger.error(f"LLM响应JSON解析失败: {e}")
            self.logger.debug(f"原始响应: {response}")
        except Exception as e:
            self.logger.error(f"LLM评分响应解析失败: {e}")
        
        # 解析失败时返回默认评分
        return [
            LLMRerankingScore(
                total_score=result.score,
                relevance_score=result.score,
                authority_score=0.5,
                quality_score=0.5,
                utility_score=0.5,
                reasoning="LLM响应解析失败",
                details={"error": "parse_failed"}
            )
            for result in results
        ] 