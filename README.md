# Awesome List Agent

## 项目简介

Awesome List Agent 是一个智能内容整理工具，能够根据用户输入的主题，自动搜索相关的文献、代码库、工具等资源，并将其整理成类似 GitHub Awesome List 的 Markdown 格式。

## 核心功能

- **智能主题扩展**：基于用户输入的主题，使用大语言模型进行联想和扩展，生成相关的子领域、概念和关键词
- **多源搜索**：集成 Tavily API，支持搜索 arXiv 论文、GitHub 代码库、技术博客等多种来源
- **智能筛选**：自动去重、质量筛选和相关性排序，确保结果的高质量
- **内容整理**：使用大模型提炼内容摘要，生成结构化的 Awesome List
- **多模型支持**：支持 OpenAI GPT 和 DeepSeek 模型切换

## 技术架构

### 后端 (Python)
- **框架**: FastAPI
- **AI 集成**: LangChain
- **搜索引擎**: Tavily API
- **大语言模型**: OpenAI GPT / DeepSeek
- **环境管理**: Pixi

### 前端 (Vue3)
- **框架**: Vue 3 (Composition API)
- **样式**: Tailwind CSS
- **Markdown 渲染**: Marked

## API 接口

### POST /api/v1/generate_awesome_list
生成 Awesome List

**请求参数:**
```json
{
  "topic": "string",  // 用户输入的主题
  "model": "gpt|deepseek"  // 可选，指定使用的大模型
}
```

**返回格式:**
```json
{
  "awesome_list": "string",  // 生成的 Markdown 格式 Awesome List
  "keywords": ["string"],   // 提取的关键词
  "total_results": "number" // 搜索结果总数
}
```

## 环境配置

需要配置以下环境变量（在 `.env` 文件中）：
```env
OPENAI_API_KEY="your_openai_api_key_here"
DEEPSEEK_API_KEY="your_deepseek_api_key_here"
TAVILY_API_KEY="your_tavily_api_key_here"
```

## 安装和运行

### 后端
```bash
# 使用 Pixi 管理环境
pixi install

# 启动后端服务
pixi run uvicorn main:app --reload
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## 项目结构

```
awesome-agent/
├── README.md           # 项目说明
├── 开发说明.md        # 详细开发文档
├── 开发进度.md        # 开发进度记录
├── pixi.toml          # Pixi 配置文件
├── .env.example       # 环境变量模板
├── main.py            # FastAPI 主程序
├── app/               # 后端应用代码
│   ├── models/        # 数据模型
│   ├── services/      # 业务逻辑服务
│   └── utils/         # 工具函数
└── frontend/          # 前端代码（Vue3 + Tailwind CSS）
```

## 开发计划

1. **后端开发** ✨ 进行中
   - [x] 项目初始化
   - [ ] 环境搭建 (Pixi)
   - [ ] FastAPI 基础架构
   - [ ] LangChain Agent 实现
   - [ ] Tavily 搜索集成
   - [ ] 大模型集成
   - [ ] API 接口开发

2. **前端开发** 📋 待开始
   - [ ] Vue3 项目搭建
   - [ ] Tailwind CSS 配置
   - [ ] 用户界面设计
   - [ ] API 调用集成
   - [ ] Markdown 渲染

3. **测试与优化** 📋 待开始
   - [ ] 功能测试
   - [ ] 性能优化
   - [ ] 错误处理完善

## 许可证

MIT License 