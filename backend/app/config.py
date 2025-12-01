"""
Configuration management for LLM Council backend
Loads environment variables and provides centralized settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "LLM_Council"
    app_version: str = "1.0.0"
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Local Model Endpoints
    llama_7b_url: str = "http://localhost:8001"
    gptj_6b_url: str = "http://localhost:8002"
    mistral_7b_url: str = "http://localhost:8003"
    deepseek_7b_url: str = "http://localhost:8004"
    
    # Local Model Configuration
    local_model_timeout: int = 120
    local_model_max_tokens: int = 2048
    local_model_temperature: float = 0.7
    
    # Remote APIs
    huggingface_api_token: str = ""
    huggingface_model: str = "EleutherAI/gpt-neo-20b"
    huggingface_api_url: str = "https://api-inference.huggingface.co/models"
    
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-pro"
    gemini_temperature: float = 0.3
    gemini_max_tokens: int = 4096
    
    # Caching
    redis_url: Optional[str] = None
    redis_password: Optional[str] = None
    redis_db: int = 0
    cache_dir: str = "./cache"
    cache_ttl: int = 3600
    enable_cache: bool = True
    
    # Performance
    max_workers: int = 4
    request_timeout: int = 120
    max_retries: int = 3
    retry_delay: int = 2
    
    enable_parallel_stage1: bool = True
    enable_parallel_reviewers: bool = True
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    cors_allow_credentials: bool = True
    
    # Model-Specific Settings
    stage1_max_tokens: int = 1024
    stage1_temperature: float = 0.7
    
    paraphrase_max_tokens: int = 512
    paraphrase_temperature: float = 0.5
    
    reviewer_max_tokens: int = 1024
    reviewer_temperature: float = 0.3
    
    chairman_max_tokens: int = 2048
    chairman_temperature: float = 0.5
    
    # Feature Flags
    enable_stage1_llama: bool = True
    enable_stage1_hf: bool = True
    enable_reviewer_a: bool = True
    enable_reviewer_b: bool = True
    enable_chairman: bool = True
    
    fallback_on_error: bool = True
    skip_failed_models: bool = True
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    # Security
    api_key_enabled: bool = False
    api_key: str = ""
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 30
    
    # Development
    reload_on_change: bool = True
    pretty_print_json: bool = True
    save_debug_outputs: bool = False
    debug_output_dir: str = "./debug_outputs"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()
