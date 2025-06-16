"""
Awesome List Agent - FastAPI 主应用程序
智能生成Awesome List的Web API服务
"""

import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.models import (
    GenerateAwesomeListRequest,
    GenerateAwesomeListResponse,
    HealthCheckResponse,
    ErrorResponse
)
from app.utils import get_settings, get_logger, AwesomeAgentException

# 获取配置和日志
settings = get_settings()
logger = get_logger(__name__)

# 创建FastAPI应用实例
app = FastAPI(
    title="Awesome List Agent",
    description="智能生成Awesome List的API服务",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    请求日志中间件
    记录所有HTTP请求的基本信息
    """
    start_time = time.time()
    
    # 记录请求开始
    logger.info(f"开始处理请求: {request.method} {request.url}")
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 记录请求完成
    logger.info(
        f"请求处理完成: {request.method} {request.url} "
        f"- 状态码: {response.status_code} "
        f"- 耗时: {process_time:.3f}s"
    )
    
    return response


@app.exception_handler(AwesomeAgentException)
async def awesome_agent_exception_handler(request: Request, exc: AwesomeAgentException):
    """
    自定义异常处理器
    处理项目中的自定义异常
    """
    logger.error(f"业务异常: {exc.message}")
    
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.message,
            details=exc.details,
            timestamp=datetime.now().isoformat()
        ).dict()
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """
    Pydantic验证异常处理器
    处理请求参数验证失败的情况
    """
    logger.error(f"参数验证失败: {exc}")
    
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="ValidationError",
            message="请求参数验证失败",
            details={"validation_errors": exc.errors()},
            timestamp=datetime.now().isoformat()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    通用异常处理器
    处理未预期的异常
    """
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="服务器内部错误，请稍后重试",
            details={},
            timestamp=datetime.now().isoformat()
        ).dict()
    )


@app.get("/", response_model=dict)
async def root():
    """
    根路径
    返回API基本信息
    """
    return {
        "name": "Awesome List Agent",
        "version": "0.1.0",
        "description": "智能生成Awesome List的API服务",
        "docs_url": "/docs",
        "health_check": "/health"
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    健康检查接口
    返回服务状态信息
    """
    return HealthCheckResponse(
        status="healthy",
        message="Awesome List Agent is running normally",
        version="0.1.0",
        timestamp=datetime.now().isoformat()
    )


@app.post("/api/v1/generate_awesome_list", response_model=GenerateAwesomeListResponse)
async def generate_awesome_list(request: GenerateAwesomeListRequest):
    """
    生成Awesome List
    
    根据用户提供的主题，智能搜索相关资源并生成Awesome List
    """
    start_time = time.time()
    logger.info(f"开始生成Awesome List，主题: {request.topic}")
    
    try:
        # 使用真实的业务服务
        from app.services import AwesomeListService
        
        service = AwesomeListService()
        response = await service.generate_awesome_list(request)
        
        processing_time = time.time() - start_time
        logger.info(f"Awesome List生成完成，总耗时: {processing_time:.3f}s")
        
        return response
        
    except Exception as e:
        logger.error(f"生成Awesome List时发生错误: {e}", exc_info=True)
        
        # 根据异常类型返回不同的错误信息
        if "API" in str(e) or "timeout" in str(e).lower():
            raise HTTPException(status_code=503, detail=f"外部服务暂不可用: {str(e)}")
        elif "模型" in str(e) or "LLM" in str(e):
            raise HTTPException(status_code=502, detail=f"AI服务错误: {str(e)}")
        else:
            raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")


@app.post("/api/v1/generate_awesome_list_intelligent", response_model=GenerateAwesomeListResponse)
async def generate_awesome_list_intelligent(request: GenerateAwesomeListRequest):
    """
    智能生成Awesome List（使用Function Calling）
    
    让大模型自主决定搜索策略，更智能地收集和整理资源
    """
    start_time = time.time()
    logger.info(f"开始智能生成Awesome List，主题: {request.topic}")
    
    try:
        # 使用智能生成服务
        from app.services import AwesomeListService
        
        service = AwesomeListService()
        response = await service.generate_awesome_list_intelligent(request)
        
        processing_time = time.time() - start_time
        logger.info(f"智能Awesome List生成完成，总耗时: {processing_time:.3f}s")
        
        return response
        
    except Exception as e:
        logger.error(f"智能生成Awesome List时发生错误: {e}", exc_info=True)
        
        # 根据异常类型返回不同的错误信息
        if "API" in str(e) or "timeout" in str(e).lower():
            raise HTTPException(status_code=503, detail=f"外部服务暂不可用: {str(e)}")
        elif "模型" in str(e) or "LLM" in str(e):
            raise HTTPException(status_code=502, detail=f"AI服务错误: {str(e)}")
        else:
            raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")


@app.get("/api/v1/search_preview/{topic}")
async def search_preview(topic: str, max_results: int = 5):
    """
    搜索预览接口（调试用）
    """
    logger.info(f"获取搜索预览: {topic}")
    
    try:
        from app.services import AwesomeListService
        
        service = AwesomeListService()
        results = await service.get_search_preview(topic, max_results)
        
        return {
            "topic": topic,
            "results": [
                {
                    "title": result.title,
                    "url": result.url,
                    "source": result.source,
                    "score": result.score,
                    "content_preview": result.content[:200] + "..." if len(result.content) > 200 else result.content
                }
                for result in results.results
            ],
            "total_count": results.total_count,
            "search_time": results.search_time
        }
        
    except Exception as e:
        logger.error(f"搜索预览失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索预览失败: {str(e)}")


@app.get("/api/v1/test_llm")
async def test_llm_connection(model: str = None):
    """
    测试LLM连接接口（调试用）
    """
    logger.info(f"测试LLM连接: {model}")
    
    try:
        from app.services import AwesomeListService
        
        service = AwesomeListService()
        result = await service.test_llm_connection(model)
        
        return result
        
    except Exception as e:
        logger.error(f"LLM连接测试失败: {e}")
        raise HTTPException(status_code=500, detail=f"LLM连接测试失败: {str(e)}")


@app.get("/api/v1/test_reranker/{topic}")
async def test_reranker(
    topic: str, 
    max_results: int = 5,
    scoring_method: str = "rule_based"
):
    """
    测试Reranker RAG功能
    
    Args:
        topic: 搜索主题
        max_results: 最大结果数量 
        scoring_method: 评分方法 ("rule_based" 或 "llm_based")
    """
    try:
        # 验证scoring_method参数
        if scoring_method not in ["rule_based", "llm_based"]:
            raise HTTPException(
                status_code=400, 
                detail="scoring_method必须是'rule_based'或'llm_based'"
            )
        
        from app.services.reranker_service import RerankerService
        from app.services.awesome_list_service import AwesomeListService
        
        # 先获取原始搜索结果
        service = AwesomeListService()
        search_results = await service.get_search_preview(topic, max_results)
        
        # 应用重排序
        reranker_service = RerankerService()
        reranked_results = await reranker_service.rerank_search_results(
            search_results=search_results,
            query=topic,
            target_count=max_results,
            scoring_method=scoring_method
        )
        
        return {
            "topic": topic,
            "scoring_method": scoring_method,
            "original_results": [
                {
                    "title": r.title,
                    "url": r.url,
                    "original_score": r.score,
                    "source": r.source
                }
                for r in search_results.results
            ],
            "reranked_results": [
                {
                    "title": r.title,
                    "url": r.url,
                    "reranked_score": r.score,
                    "source": r.source
                }
                for r in reranked_results.results
            ],
            "reranking_applied": reranked_results.filters_applied.get("reranked", False),
            "scoring_method_used": reranked_results.filters_applied.get("scoring_method", "rule_based"),
            "reranking_weights": reranked_results.filters_applied.get("reranking_weights", {}),
            "processing_time": reranked_results.search_time,
            "score_changes": [
                {
                    "title": orig.title,
                    "original_score": orig.score,
                    "reranked_score": reranked.score,
                    "change": reranked.score - orig.score
                }
                for orig, reranked in zip(search_results.results, reranked_results.results)
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reranker测试失败: {str(e)}")


@app.get("/api/v1/debug_function_calling/{topic}")
async def debug_function_calling(topic: str):
    """
    调试Function Calling功能
    """
    try:
        from app.services.intelligent_search_service import IntelligentSearchService
        
        service = IntelligentSearchService()
        
        # 直接调用搜索计划生成
        search_plan = await service._generate_search_plan(
            topic=topic,
            language="zh",
            model="deepseek"
        )
        
        return {
            "topic": topic,
            "search_plan_count": len(search_plan),
            "search_plan": search_plan,
            "plan_details": [
                {
                    "query": plan.get("query", ""),
                    "search_type": plan.get("search_type", ""),
                    "max_results": plan.get("max_results", 0)
                }
                for plan in search_plan
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Function Calling调试失败: {str(e)}")


@app.get("/api/v1/test_model_calling/{topic}")
async def test_model_calling(topic: str, model: str = "gpt"):
    """
    直接测试模型的Function Calling能力，不使用降级策略
    """
    try:
        from app.services.intelligent_search_service import IntelligentSearchService
        
        service = IntelligentSearchService()
        
        # 直接调用搜索计划生成，不使用降级
        search_plan = []
        try:
            search_plan = await service._generate_search_plan(
                topic=topic,
                language="zh",
                model=model
            )
        except Exception as e:
            return {
                "error": str(e),
                "topic": topic,
                "model": model,
                "search_plan_count": 0,
                "message": "Function Calling失败"
            }
        
        # 检查是否使用了降级策略
        is_fallback = len(search_plan) == 4 and all(
            plan.get("search_type") in ["arxiv_papers", "github_repos", "research_code", "huggingface_models"] 
            for plan in search_plan
        )
        
        return {
            "topic": topic,
            "model": model,
            "search_plan_count": len(search_plan),
            "is_fallback_strategy": is_fallback,
            "plan_details": search_plan,
            "success": len(search_plan) > 0 and not is_fallback
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型调用测试失败: {str(e)}")


@app.get("/api/v1/academic_info")
async def get_academic_info():
    """
    获取学术模式信息
    """
    return {
        "mode": "Academic Research Mode",
        "description": "专为科研和学术领域优化的Awesome List生成器",
        "search_domains": ["arxiv.org", "github.com", "huggingface.co"],
        "search_types": [
            "arxiv_papers - arXiv论文搜索",
            "github_repos - GitHub代码库搜索", 
            "huggingface_models - Hugging Face模型搜索",
            "research_code - 研究代码搜索",
            "academic_datasets - 学术数据集搜索",
            "conference_papers - 会议论文搜索"
        ],
        "features": [
            "Function Calling智能搜索策略",
            "多模型支持 (GPT-4-Turbo, DeepSeek)",
            "学术资源优先级排序",
            "自动关键词提取",
            "中英文双语支持"
        ],
        "apis": {
            "intelligent": "/api/v1/generate_awesome_list_intelligent",
            "traditional": "/api/v1/generate_awesome_list",
            "search_preview": "/api/v1/search_preview/{topic}",
            "llm_test": "/api/v1/test_llm"
        }
    }


@app.post("/api/v1/save_markdown")
async def save_markdown(request: dict):
    """
    保存Awesome List为本地markdown文件
    """
    try:
        topic = request.get("topic", "awesome-list")
        content = request.get("content", "")
        
        if not content:
            raise HTTPException(status_code=400, detail="内容不能为空")
        
        # 清理文件名，移除特殊字符
        import re
        safe_filename = re.sub(r'[^\w\s-]', '', topic.strip())
        safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
        filename = f"awesome-{safe_filename.lower()}.md"
        
        # 保存到当前目录
        filepath = f"./{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "message": f"文件已保存",
            "filename": filename,
            "filepath": filepath,
            "size": len(content)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")


@app.post("/api/v1/generate_and_save")
async def generate_and_save(request: GenerateAwesomeListRequest):
    """
    生成Awesome List并自动保存为本地文件
    """
    try:
        # 生成Awesome List
        result = await awesome_list_service.generate_awesome_list_intelligent(request)
        
        # 保存到本地文件
        import re
        safe_filename = re.sub(r'[^\w\s-]', '', request.topic.strip())
        safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
        filename = f"awesome-{safe_filename.lower()}.md"
        filepath = f"./{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result.awesome_list)
        
        return {
            **result.dict(),
            "saved_to_file": True,
            "filename": filename,
            "filepath": filepath
        }
        
    except Exception as e:
        logger.error(f"生成并保存失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成并保存失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("启动Awesome List Agent服务...")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    ) 