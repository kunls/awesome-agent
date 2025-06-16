# Awesome List Agent 大模型 Prompt 汇报文档

## 📋 文档概览

本文档整理了 **Awesome List Agent** 项目中所有使用的大模型 Prompt 模板，涵盖了四大核心功能模块的智能交互设计。这些 Prompt 是项目 AI 能力的核心，体现了从用户需求理解到结果生成的完整智能化流程。

## 🎯 项目背景

Awesome List Agent 是一个基于 AI 的学术资源整理工具，采用传统搜索和智能搜索双模式，集成了多个大模型 API，通过精心设计的 Prompt 工程实现高质量的学术资源发现和组织。

## 🔍 Prompt 分类概览

| 模块 | Prompt 数量 | 主要功能 | 支持语言 |
|------|------------|---------|----------|
| 主题扩展 | 2个 | 关键词挖掘、概念扩展 | 中文/英文 |
| 智能搜索 | 2个 | 搜索策略制定、Function Calling | 中文/英文 |
| 结果评分 | 1个 | 多维度智能评分 | 中文 |
| 内容生成 | 2个 | Awesome List 生成 | 中文/英文 |
| 关键词提取 | 1个 | JSON 格式关键词提取 | 中文 |
| **总计** | **8个** | **完整 AI 工作流** | **双语支持** |

---

## 📚 模块一：主题扩展 Prompt

### 1.1 功能说明
主题扩展模块负责将用户输入的简单主题扩展为丰富的关键词、相关概念和搜索查询，为后续智能搜索提供基础。

### 1.2 中文版 Prompt
```markdown
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
```

### 1.3 英文版 Prompt
```markdown
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
```

### 1.4 设计亮点
- **结构化输出**：采用固定格式确保解析准确性
- **多维度扩展**：关键词、概念、查询三个维度全覆盖
- **质量导向**：明确要求"高质量资源"，提升搜索效果
- **数量控制**：3-5个项目的限制避免信息过载

---

## 🔍 模块二：智能搜索 Prompt

### 2.1 功能说明
智能搜索模块使用 Function Calling 技术，让大模型自主制定搜索策略，根据主题特点选择最适合的搜索类型和查询方式。

### 2.2 中文版 Prompt
```markdown
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
```

### 2.3 英文版 Prompt
```markdown
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
```

### 2.4 设计亮点
- **强制工具调用**：明确要求使用工具而非文字回答
- **多角度搜索**：要求3-4次搜索覆盖不同角度
- **学术导向**：五种搜索类型全面覆盖学术资源
- **即时执行**：强调"立即开始搜索"，提高执行效率

---

## 📊 模块三：LLM 智能评分 Prompt

### 3.1 功能说明
LLM评分模块对搜索结果进行多维度智能评估，从相关性、权威性、质量、实用性四个维度提供精确评分。

### 3.2 完整 Prompt
```markdown
你是一个专业的学术搜索结果评分专家。请为以下搜索结果进行多维度评分。

查询词: "{query}"

搜索结果:
{搜索结果详细信息}

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

{
  "scores": [
    {
      "result_index": 1,
      "relevance_score": 0.85,
      "authority_score": 0.90,
      "quality_score": 0.80,
      "utility_score": 0.88,
      "reasoning": "详细说明评分理由"
    },
    {
      "result_index": 2,
      "relevance_score": 0.75,
      "authority_score": 0.70,
      "quality_score": 0.85,
      "utility_score": 0.80,
      "reasoning": "详细说明评分理由"
    }
  ]
}

评分标准：
- 0.9-1.0: 优秀
- 0.8-0.9: 良好  
- 0.7-0.8: 一般
- 0.6-0.7: 较差
- 0.0-0.6: 很差
```

### 3.3 设计亮点
- **四维评分体系**：相关性、权威性、质量、实用性全面覆盖
- **详细评分标准**：每个维度都有明确的评价指标
- **标准化输出**：严格的JSON格式确保结果可解析
- **质量控制**：0.1-1.0的评分区间和五级质量标准

---

## 📝 模块四：Awesome List 生成 Prompt

### 4.1 功能说明
Awesome List生成模块将搜索结果整理成标准的Markdown格式列表，确保内容结构清晰、专业规范。

### 4.2 中文版 Prompt
```markdown
你是一个技术资源整理专家。请根据以下搜索结果，生成一个高质量的 Awesome {topic} 列表。

搜索结果：
{搜索结果摘要}

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
```

### 4.3 英文版 Prompt
```markdown
You are a technical resource curator. Please generate a high-quality Awesome {topic} list based on the following search results.

Search Results:
{搜索结果摘要}

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
```

### 4.4 设计亮点
- **标准化格式**：严格遵循GitHub Awesome List规范
- **分类组织**：官方资源、工具库、文档、示例等清晰分类
- **视觉优化**：emoji图标提升阅读体验
- **质量优先**：强调权威性和准确性

---

## 🔤 模块五：关键词提取 Prompt

### 5.1 功能说明
关键词提取模块从生成的Awesome List中提取核心关键词，用于前端标签显示。

### 5.2 Prompt 内容
```markdown
请从以下文本中提取最重要的 {max_keywords} 个关键词，返回JSON格式：

文本：
{text[:1000]}  # 限制文本长度

请返回格式：
{"keywords": ["关键词1", "关键词2", ...]}
```

### 5.3 设计亮点
- **数量控制**：动态设置关键词数量
- **长度限制**：文本截断避免处理过长内容
- **JSON输出**：标准化格式便于解析
- **容错机制**：JSON解析失败时使用文本分割备选方案

---

## 📊 Prompt 工程技术总结

### 1. 技术特点

| 技术要素 | 应用场景 | 具体体现 |
|---------|---------|---------|
| **结构化输出** | 全部模块 | 固定格式、JSON输出、标准化模板 |
| **多语言支持** | 主要模块 | 中英文双版本，保持逻辑一致性 |
| **Function Calling** | 智能搜索 | 工具调用、参数传递、结果解析 |
| **上下文注入** | 内容生成 | 搜索结果摘要、主题信息整合 |
| **约束性指令** | 智能评分 | 严格JSON格式、评分标准明确 |

### 2. 质量保证机制

- **明确角色定义**：每个Prompt都有专业角色设定
- **详细操作指令**：步骤化、可执行的具体要求
- **输出格式约束**：JSON、Markdown等标准化格式
- **容错处理**：解析失败时的降级方案
- **双语一致性**：中英文版本逻辑完全对应

### 3. 创新亮点

- **自适应搜索策略**：大模型自主制定搜索计划
- **多维度评分体系**：四个维度的综合智能评估
- **学术资源特化**：针对学术场景的专门优化
- **端到端智能化**：从需求理解到结果生成的全流程AI化

---

## 🎯 应用效果与价值

### 1. 技术价值
- **Prompt工程最佳实践**：展示了企业级Prompt设计方法
- **多模型协同**：GPT-4、DeepSeek等模型的有效整合
- **Function Calling应用**：实际生产环境中的工具调用示例

### 2. 业务价值
- **效率提升**：传统人工整理 2-3 小时 → AI生成 30-60 秒
- **质量保证**：多维度评分确保资源权威性和实用性
- **覆盖全面**：五种搜索类型覆盖学术资源全景

### 3. 教育价值
- **课程作业优秀案例**：展示AI应用的完整实现
- **技术学习参考**：Prompt工程、API集成、系统设计的综合示例
- **行业应用思路**：AI在内容整理和知识管理领域的应用探索

---

## 📈 未来优化方向

1. **Prompt 自优化**：基于使用效果自动调整Prompt参数
2. **多模态扩展**：支持图像、视频等多媒体资源的智能处理
3. **个性化定制**：根据用户领域和偏好定制专门的Prompt版本
4. **实时学习**：结合用户反馈持续优化Prompt效果

---

## 📝 总结

Awesome List Agent 的 Prompt 设计体现了现代 AI 应用开发的最佳实践：

- **系统性设计**：8个精心设计的Prompt覆盖完整工作流
- **工程化实现**：结构化、标准化、可维护的Prompt架构  
- **实用性导向**：面向实际业务需求的技术选择
- **创新性突破**：Function Calling、多维评分等先进技术应用

这套Prompt体系不仅成功实现了项目目标，更为AI应用开发提供了宝贵的参考模板和实践经验。

---

*本文档生成时间：2024年12月* | *Awesome List Agent v1.0* 