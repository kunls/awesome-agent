"""
大语言模型服务模块
集成OpenAI和DeepSeek API实现智能内容生成
"""

import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

import openai
import httpx

from app.models import ExtendedTopic, SearchResults
from app.utils import get_settings, get_logger, LLMException, APIException, LoggerMixin


class LLMService(LoggerMixin):
    """
    大语言模型服务类
    负责集成多个LLM提供商进行智能内容生成
    """

    def __init__(self):
        self.settings = get_settings()

        # 初始化OpenAI客户端
        self.openai_client = openai.AsyncOpenAI(
            api_key=self.settings.openai_api_key,
            timeout=self.settings.request_timeout
        )

        # DeepSeek使用OpenAI兼容的API
        self.deepseek_client = openai.AsyncOpenAI(
            api_key=self.settings.deepseek_api_key,
            base_url="https://api.deepseek.com/v1",
            timeout=self.settings.request_timeout
        )

    async def expand_topic(self, topic: str, language: str = "zh") -> ExtendedTopic:
        """
        扩展主题，生成相关关键词和搜索查询

        Args:
            topic: 原始主题
            language: 语言 (zh/en)

        Returns:
            ExtendedTopic: 扩展后的主题信息
        """
        self.logger.info(f"🔍 开始扩展主题: {topic}")

        try:
            prompt = self._build_topic_expansion_prompt(topic, language)

            # 使用默认模型进行主题扩展
            response = await self._call_llm(
                model=self.settings.default_llm_model,
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )

            # 记录LLM原始响应
            self.logger.info(f"📝 主题扩展原始响应:\n{response}")

            # 解析响应
            expanded_topic = self._parse_topic_expansion_response(
                response, topic)

            # 详细记录扩展结果
            self.logger.info(f"✅ 主题扩展完成!")
            self.logger.info(f"🔑 扩展关键词 ({len(expanded_topic.extended_keywords)}个): {expanded_topic.extended_keywords}")
            self.logger.info(f"💡 相关概念 ({len(expanded_topic.related_concepts)}个): {expanded_topic.related_concepts}")
            self.logger.info(f"🔍 搜索查询 ({len(expanded_topic.search_queries)}个): {expanded_topic.search_queries}")
            
            return expanded_topic

        except Exception as e:
            self.logger.error(f"❌ 主题扩展失败: {e}", exc_info=True)
            # 返回默认的扩展结果，但记录详细信息
            fallback_topic = ExtendedTopic(
                original_topic=topic,
                extended_keywords=[topic],
                related_concepts=[],
                search_queries=[topic, f"{topic} tutorial", f"awesome {topic}"]
            )
            self.logger.warning(f"🔄 使用默认扩展结果: {fallback_topic.extended_keywords}")
            return fallback_topic

    async def generate_awesome_list(
        self,
        topic: str,
        search_results: SearchResults,
        language: str = "zh",
        model: str = None
    ) -> str:
        """
        根据搜索结果生成Awesome List

        Args:
            topic: 主题
            search_results: 搜索结果
            language: 语言
            model: 指定的模型

        Returns:
            str: 生成的Markdown格式Awesome List
        """
        self.logger.info(f"开始生成Awesome List: {topic}")

        try:
            prompt = self._build_awesome_list_prompt(
                topic, search_results, language)

            used_model = model or self.settings.default_llm_model

            response = await self._call_llm(
                model=used_model,
                prompt=prompt,
                max_tokens=2000,
                temperature=0.3  # 较低的温度以获得更稳定的输出
            )

            # 后处理生成的内容
            awesome_list = self._post_process_awesome_list(response, topic)

            self.logger.info(f"Awesome List生成完成，长度: {len(awesome_list)} 字符")
            return awesome_list

        except Exception as e:
            self.logger.error(f"Awesome List生成失败: {e}")
            raise LLMException(f"生成Awesome List失败: {str(e)}")

    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        从文本中提取关键词

        Args:
            text: 输入文本
            max_keywords: 最大关键词数量

        Returns:
            List[str]: 关键词列表
        """
        try:
            prompt = f"""
请从以下文本中提取最重要的 {max_keywords} 个关键词，返回JSON格式：

文本：
{text[:1000]}  # 限制文本长度

请返回格式：
{{"keywords": ["关键词1", "关键词2", ...]}}
"""

            response = await self._call_llm(
                model=self.settings.default_llm_model,
                prompt=prompt,
                max_tokens=200,
                temperature=0.1
            )

            # 简单解析关键词
            import json
            try:
                parsed = json.loads(response)
                return parsed.get("keywords", [])[:max_keywords]
            except json.JSONDecodeError:
                # 如果JSON解析失败，使用简单的文本分割
                keywords = [word.strip().strip('"\'')
                            for word in response.split('\n') if word.strip()]
                return keywords[:max_keywords]

        except Exception as e:
            self.logger.warning(f"关键词提取失败: {e}")
            return []

    async def _call_llm(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto"
    ) -> str:
        """
        调用指定的大语言模型

        Args:
            model: 模型名称 (gpt/deepseek)
            prompt: 提示词
            max_tokens: 最大令牌数
            temperature: 温度参数
            tools: 工具定义列表（Function Calling）
            tool_choice: 工具选择策略

        Returns:
            str: 模型响应
        """
        try:
            # 记录模型调用信息
            tools_info = f"，工具数量: {len(tools) if tools else 0}" if tools else ""
            self.logger.info(
                f"🔧 调用LLM: {model.upper()}{tools_info}，温度: {temperature}")
            # 构建请求参数
            messages = [{"role": "user", "content": prompt}]
            request_params = {
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            # 添加工具定义（如果提供）
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = tool_choice

            if model.lower() == "gpt":
                # 使用GPT-4 Turbo，Function Calling能力更强
                actual_model = "gpt-4-turbo-preview"
                self.logger.info(
                    f"📡 实际调用模型: {actual_model} (支持强化Function Calling)")
                response = await self.openai_client.chat.completions.create(
                    model=actual_model,
                    **request_params
                )
                return self._process_llm_response(response)

            elif model.lower() == "deepseek":
                actual_model = "deepseek-chat"
                self.logger.debug(f"📡 实际调用模型: {actual_model}")
                response = await self.deepseek_client.chat.completions.create(
                    model=actual_model,
                    **request_params
                )
                return self._process_llm_response(response)

            else:
                raise LLMException(f"不支持的模型: {model}")

        except Exception as e:
            self.logger.error(f"LLM调用失败 ({model}): {e}")
            raise APIException(f"LLM API调用失败: {str(e)}")

    def _process_llm_response(self, response) -> str:
        """
        处理LLM响应，支持Function Calling
        """
        choice = response.choices[0]
        message = choice.message

        # 如果是普通文本响应
        if message.content:
            return message.content

        # 如果是工具调用响应
        if hasattr(message, 'tool_calls') and message.tool_calls:
            # 返回工具调用信息的JSON字符串
            import json
            tool_calls = []
            for tool_call in message.tool_calls:
                tool_calls.append({
                    "id": tool_call.id,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                })
            return json.dumps({"tool_calls": tool_calls})

        return ""

    def _build_topic_expansion_prompt(self, topic: str, language: str) -> str:
        """
        构建主题扩展的提示词
        """
        if language == "zh":
            return f"""
你是一个主题研究专家。请帮我扩展以下主题，生成相关的关键词、概念和搜索查询。

主题：{topic}

请按以下格式返回：

扩展关键词：
- 关键词1
- 关键词2
- 关键词3

相关概念：
- 概念1
- 概念2
- 概念3

推荐搜索查询：
- 查询1
- 查询2
- 查询3

要求：
1. 关键词应该涵盖主题的不同方面
2. 相关概念应该是与主题相关的技术术语或概念
3. 搜索查询应该能够找到高质量的资源
4. 每类提供3-5个项目即可
"""
        else:
            return f"""
You are a topic research expert. Please help me expand the following topic by generating related keywords, concepts, and search queries.

Topic: {topic}

Please return in the following format:

Extended Keywords:
- keyword1
- keyword2
- keyword3

Related Concepts:
- concept1
- concept2
- concept3

Recommended Search Queries:
- query1
- query2
- query3

Requirements:
1. Keywords should cover different aspects of the topic
2. Related concepts should be technical terms or concepts related to the topic
3. Search queries should be able to find high-quality resources
4. Provide 3-5 items for each category
"""

    def _build_awesome_list_prompt(
        self,
        topic: str,
        search_results: SearchResults,
        language: str
    ) -> str:
        """
        构建生成Awesome List的提示词
        """
        # 准备搜索结果摘要
        results_summary = []
        for i, result in enumerate(search_results.results[:10], 1):  # 限制结果数量
            results_summary.append(
                f"{i}. [{result.title}]({result.url}) - {result.source} - {result.content[:200]}..."
            )

        results_text = "\n".join(results_summary)

        if language == "zh":
            return f"""
你是一个技术资源整理专家。请根据以下搜索结果，生成一个高质量的 Awesome {topic} 列表。

搜索结果：
{results_text}

请生成一个Markdown格式的Awesome List，要求：

1. 使用标准的Awesome List格式
2. 包含清晰的分类（如：官方资源、工具库、教程文档、项目示例等）
3. 每个链接都要有简洁的描述
4. 优先选择最权威和有用的资源
5. 确保链接的准确性
6. 添加适当的emoji图标
7. 包含简介部分
8. 保持专业和准确

格式示例：
# Awesome {topic}

> 精选的 {topic} 相关资源列表

## 📚 官方资源
- [资源名称](链接) - 简洁描述

## 🛠️ 工具和库
- [工具名称](链接) - 简洁描述

请确保生成的内容准确、有用且结构清晰。
"""
        else:
            return f"""
You are a technical resource curator. Please generate a high-quality Awesome {topic} list based on the following search results.

Search Results:
{results_text}

Please generate a Markdown-formatted Awesome List with the following requirements:

1. Use standard Awesome List format
2. Include clear categories (e.g., Official Resources, Tools & Libraries, Documentation, Examples)
3. Each link should have a concise description
4. Prioritize the most authoritative and useful resources
5. Ensure link accuracy
6. Add appropriate emoji icons
7. Include an introduction section
8. Maintain professionalism and accuracy

Format example:
# Awesome {topic}

> A curated list of {topic} resources

## 📚 Official Resources
- [Resource Name](link) - Brief description

## 🛠️ Tools & Libraries
- [Tool Name](link) - Brief description

Please ensure the generated content is accurate, useful, and well-structured.
"""

    def _parse_topic_expansion_response(self, response: str, original_topic: str) -> ExtendedTopic:
        """
        解析主题扩展响应
        """
        try:
            self.logger.info(f"🔍 开始解析主题扩展响应...")
            lines = response.strip().split('\n')

            extended_keywords = []
            related_concepts = []
            search_queries = []

            current_section = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if "扩展关键词" in line or "Extended Keywords" in line:
                    current_section = "keywords"
                    self.logger.debug(f"📝 进入扩展关键词部分")
                elif "相关概念" in line or "Related Concepts" in line:
                    current_section = "concepts"
                    self.logger.debug(f"📝 进入相关概念部分")
                elif "搜索查询" in line or "Search Queries" in line or "推荐搜索查询" in line or "Recommended Search Queries" in line:
                    current_section = "queries"
                    self.logger.debug(f"📝 进入搜索查询部分")
                elif line.startswith('- '):
                    item = line[2:].strip()
                    # 过滤掉空字符串
                    if not item:
                        self.logger.debug(f"⚠️ 跳过空项目")
                        continue
                        
                    if current_section == "keywords":
                        extended_keywords.append(item)
                        self.logger.debug(f"🔑 添加关键词: {item}")
                    elif current_section == "concepts":
                        related_concepts.append(item)
                        self.logger.debug(f"💡 添加概念: {item}")
                    elif current_section == "queries":
                        search_queries.append(item)
                        self.logger.debug(f"🔍 添加查询: {item}")

            # 过滤掉所有空字符串
            extended_keywords = [kw for kw in extended_keywords if kw and kw.strip()]
            related_concepts = [concept for concept in related_concepts if concept and concept.strip()]
            search_queries = [query for query in search_queries if query and query.strip()]

            # 记录解析统计
            self.logger.info(f"📊 解析统计 - 关键词:{len(extended_keywords)}, 概念:{len(related_concepts)}, 查询:{len(search_queries)}")

            # 确保包含原始主题
            if original_topic and original_topic not in extended_keywords:
                extended_keywords.insert(0, original_topic)
                self.logger.debug(f"🔄 添加原始主题到关键词: {original_topic}")

            # 如果解析失败，提供默认值
            if not extended_keywords:
                extended_keywords = [original_topic] if original_topic else ["general topic"]
                self.logger.warning(f"⚠️ 未解析到关键词，使用默认值: {extended_keywords}")
            if not search_queries:
                search_queries = [original_topic, f"{original_topic} tutorial"] if original_topic else ["general search"]
                self.logger.warning(f"⚠️ 未解析到查询，使用默认值: {search_queries}")

            result = ExtendedTopic(
                original_topic=original_topic,
                extended_keywords=extended_keywords,
                related_concepts=related_concepts,
                search_queries=search_queries
            )
            
            self.logger.info(f"✅ 主题扩展响应解析完成")
            self.logger.info(f"🎯 最终关键词: {result.extended_keywords}")
            self.logger.info(f"🎯 最终概念: {result.related_concepts}")
            
            return result

        except Exception as e:
            self.logger.error(f"❌ 解析主题扩展响应失败: {e}", exc_info=True)
            fallback_result = ExtendedTopic(
                original_topic=original_topic,
                extended_keywords=[original_topic] if original_topic else ["fallback topic"],
                related_concepts=[],
                search_queries=[original_topic, f"{original_topic} tutorial", f"awesome {original_topic}"] if original_topic else ["fallback search"]
            )
            self.logger.warning(f"🔄 使用解析失败时的默认结果: {fallback_result.extended_keywords}")
            return fallback_result

    def _post_process_awesome_list(self, content: str, topic: str) -> str:
        """
        后处理生成的Awesome List
        """
        # 确保有标题
        if not content.startswith("#"):
            content = f"# Awesome {topic}\n\n{content}"

        # 确保有生成标识
        if "Awesome List Agent" not in content:
            content += "\n\n---\n*由 Awesome List Agent 智能生成*"

        return content.strip()
