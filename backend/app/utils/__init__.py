"""
Logging utilities for LLM Council
"""

import sys
import json
from datetime import datetime
from pathlib import Path
from loguru import logger
from app.config import settings


def setup_logger():
    """Configure loguru logger"""
    
    # Remove default handler
    logger.remove()
    
    # Console handler with custom format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True
    )
    
    # File handler for errors
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "error.log",
        level="ERROR",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        format=log_format
    )
    
    # File handler for all logs
    logger.add(
        log_dir / "app.log",
        level="DEBUG" if settings.debug_mode else "INFO",
        rotation="50 MB",
        retention="7 days",
        compression="zip",
        format=log_format
    )
    
    return logger


def log_request(request_id: str, query: str, options: dict):
    """Log incoming request"""
    logger.info(f"[{request_id}] New query received: {query[:100]}...")
    logger.debug(f"[{request_id}] Options: {json.dumps(options)}")


def log_response(request_id: str, status: str, processing_time: float, error: str = None):
    """Log response"""
    if status == "success":
        logger.info(f"[{request_id}] Query completed successfully in {processing_time:.2f}s")
    else:
        logger.error(f"[{request_id}] Query failed after {processing_time:.2f}s: {error}")


def log_stage(request_id: str, stage_name: str, status: str, duration: float = None):
    """Log pipeline stage"""
    if duration:
        logger.info(f"[{request_id}] Stage '{stage_name}' {status} in {duration:.2f}s")
    else:
        logger.info(f"[{request_id}] Stage '{stage_name}' {status}")


def log_model_call(request_id: str, model_name: str, status: str, duration: float = None):
    """Log model API call"""
    if status == "success":
        logger.debug(f"[{request_id}] {model_name} responded in {duration:.2f}s")
    elif status == "failed":
        logger.warning(f"[{request_id}] {model_name} call failed after {duration:.2f}s")
    else:
        logger.debug(f"[{request_id}] {model_name} call {status}")
