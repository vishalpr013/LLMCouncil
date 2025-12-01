"""
Error handling utilities
"""

from typing import Dict, Any
from fastapi import HTTPException
import traceback
from app.utils.logger import logger


class PipelineError(Exception):
    """Base exception for pipeline errors"""
    pass


class ModelTimeoutError(PipelineError):
    """Model request timeout"""
    pass


class ModelAPIError(PipelineError):
    """Model API call failed"""
    pass


class ValidationError(PipelineError):
    """Response validation failed"""
    pass


def handle_pipeline_error(error: Exception, request_id: str, processing_time: float) -> Dict[str, Any]:
    """
    Handle pipeline errors and return structured error response
    """
    
    error_type = type(error).__name__
    error_message = str(error)
    
    logger.error(f"[{request_id}] Pipeline error: {error_type} - {error_message}")
    logger.debug(f"[{request_id}] Traceback: {traceback.format_exc()}")
    
    # Determine status code based on error type
    if isinstance(error, ModelTimeoutError):
        status_code = 504
        detail = f"Model request timed out: {error_message}"
    elif isinstance(error, ModelAPIError):
        status_code = 502
        detail = f"Model API error: {error_message}"
    elif isinstance(error, ValidationError):
        status_code = 422
        detail = f"Validation error: {error_message}"
    elif isinstance(error, ValueError):
        status_code = 400
        detail = f"Invalid input: {error_message}"
    else:
        status_code = 500
        detail = f"Internal server error: {error_message}"
    
    return {
        "status_code": status_code,
        "detail": {
            "error": error_type,
            "message": detail,
            "request_id": request_id,
            "processing_time": processing_time
        }
    }


def safe_execute(func, *args, fallback=None, error_msg="Operation failed", **kwargs):
    """
    Safely execute a function with error handling and fallback
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"{error_msg}: {str(e)}")
        if fallback is not None:
            return fallback
        raise
