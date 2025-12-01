"""
FastAPI Main Application Entry Point
Orchestrates the multi-model debate pipeline
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from typing import Dict, Any

from app.config import settings
from app.models.schemas import QueryRequest, QueryResponse, HealthResponse
from app.services.orchestrator import PipelineOrchestrator
from app.utils.logger import setup_logger, log_request, log_response
from app.utils.error_handler import handle_pipeline_error

# Setup logger
logger = setup_logger()

# Initialize orchestrator
orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the application"""
    global orchestrator
    
    logger.info("🚀 Starting LLM Council Backend...")
    logger.info(f"Version: {settings.app_version}")
    logger.info(f"Debug Mode: {settings.debug_mode}")
    
    # Initialize orchestrator
    orchestrator = PipelineOrchestrator()
    await orchestrator.initialize()
    
    logger.info("✅ LLM Council Backend started successfully")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down LLM Council Backend...")
    await orchestrator.cleanup()
    logger.info("✅ Cleanup completed")


# Create FastAPI app
app = FastAPI(
    title="LLM Council API",
    description="Multi-model debate pipeline for high-quality answer generation",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "LLM Council API",
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns status of all models and services
    """
    try:
        health_status = await orchestrator.check_health()
        return HealthResponse(**health_status)
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/api/query", response_model=QueryResponse, tags=["Pipeline"])
async def process_query(request: QueryRequest):
    """
    Main pipeline endpoint
    Processes a user query through the entire multi-model debate pipeline
    
    Pipeline stages:
    1. Stage-1: Parallel first opinions (Llama-7B + GPT-OSS-20B)
    2. Paraphrase: Claim extraction (GPT-J-6B)
    3. Review: Peer review (Mistral-7B + DeepSeek-7B)
    4. Aggregation: Combine verdicts
    5. Chairman: Final synthesis (Gemini)
    """
    start_time = time.time()
    request_id = f"req_{int(start_time * 1000)}"
    
    log_request(request_id, request.query, request.options)
    
    try:
        # Run the pipeline
        result = await orchestrator.run_pipeline(
            query=request.query,
            options=request.options,
            request_id=request_id
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        result["metadata"]["processing_time"] = processing_time
        result["metadata"]["request_id"] = request_id
        
        log_response(request_id, "success", processing_time)
        
        return QueryResponse(**result)
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_response = handle_pipeline_error(e, request_id, processing_time)
        log_response(request_id, "error", processing_time, str(e))
        
        raise HTTPException(
            status_code=error_response["status_code"],
            detail=error_response["detail"]
        )


@app.get("/api/models", tags=["Info"])
async def list_models():
    """
    List all models used in the pipeline
    """
    return {
        "stage1_models": [
            {
                "name": "Llama-7B",
                "type": "local",
                "endpoint": settings.llama_7b_url,
                "role": "first_opinion"
            },
            {
                "name": "GPT-OSS-20B",
                "type": "remote",
                "provider": "huggingface",
                "role": "first_opinion"
            }
        ],
        "paraphrase_model": {
            "name": "GPT-J-6B",
            "type": "local",
            "endpoint": settings.gptj_6b_url,
            "role": "claim_extraction"
        },
        "reviewer_models": [
            {
                "name": "Mistral-7B-Distill",
                "type": "local",
                "endpoint": settings.mistral_7b_url,
                "role": "reviewer_a"
            },
            {
                "name": "DeepSeek-R1-Distill-7B",
                "type": "local",
                "endpoint": settings.deepseek_7b_url,
                "role": "reviewer_b"
            }
        ],
        "chairman_model": {
            "name": "Gemini-1.5-Pro",
            "type": "remote",
            "provider": "google",
            "role": "final_synthesis"
        }
    }


@app.get("/api/stats", tags=["Info"])
async def get_statistics():
    """
    Get pipeline statistics and metrics
    """
    try:
        stats = await orchestrator.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


@app.post("/api/cache/clear", tags=["Admin"])
async def clear_cache():
    """
    Clear the response cache
    """
    try:
        await orchestrator.clear_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Failed to clear cache: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug_mode else "An unexpected error occurred",
            "path": str(request.url)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.reload_on_change,
        log_level=settings.log_level.lower()
    )
