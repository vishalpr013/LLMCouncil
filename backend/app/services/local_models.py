"""
Local model runners for llama.cpp servers
Handles communication with local GGUF models
"""

import httpx
import json
import asyncio
from typing import Dict, Any, Optional
from app.config import settings
from app.utils.logger import logger
from app.utils.error_handler import ModelAPIError, ModelTimeoutError


class LocalModelRunner:
    """Base class for local model inference"""
    
    def __init__(self, model_name: str, endpoint_url: str, timeout: int = None):
        self.model_name = model_name
        self.endpoint_url = endpoint_url
        self.timeout = timeout or settings.local_model_timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)
    
    async def generate(self, prompt: dict) -> str:
        """
        Generate response from local model
        
        Args:
            prompt: Prompt configuration dict with 'prompt', 'temperature', etc.
            
        Returns:
            Generated text response
        """
        try:
            logger.debug(f"Calling {self.model_name} at {self.endpoint_url}")
            
            # llama.cpp compatible endpoint
            response = await self.client.post(
                f"{self.endpoint_url}/completion",
                json=prompt
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract generated text
            if "content" in result:
                generated_text = result["content"]
            elif "choices" in result and len(result["choices"]) > 0:
                generated_text = result["choices"][0].get("text", "")
            else:
                generated_text = result.get("text", str(result))
            
            logger.debug(f"{self.model_name} response: {generated_text[:100]}...")
            return generated_text.strip()
            
        except httpx.TimeoutException as e:
            logger.error(f"{self.model_name} timeout: {str(e)}")
            raise ModelTimeoutError(f"{self.model_name} request timed out")
            
        except httpx.HTTPStatusError as e:
            logger.error(f"{self.model_name} HTTP error: {e.response.status_code}")
            raise ModelAPIError(f"{self.model_name} returned status {e.response.status_code}")
            
        except Exception as e:
            logger.error(f"{self.model_name} error: {str(e)}")
            raise ModelAPIError(f"{self.model_name} call failed: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check if model server is healthy"""
        try:
            response = await self.client.get(
                f"{self.endpoint_url}/health",
                timeout=5.0
            )
            return response.status_code == 200
        except Exception:
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class Llama7BRunner(LocalModelRunner):
    """Runner for Llama-7B model"""
    
    def __init__(self):
        super().__init__(
            model_name="Llama-7B",
            endpoint_url=settings.llama_7b_url
        )


class GPTJ6BRunner(LocalModelRunner):
    """Runner for GPT-J-6B model (paraphrase)"""
    
    def __init__(self):
        super().__init__(
            model_name="GPT-J-6B",
            endpoint_url=settings.gptj_6b_url
        )


class Mistral7BRunner(LocalModelRunner):
    """Runner for Mistral-7B-Distill (Reviewer A)"""
    
    def __init__(self):
        super().__init__(
            model_name="Mistral-7B",
            endpoint_url=settings.mistral_7b_url
        )


class DeepSeek7BRunner(LocalModelRunner):
    """Runner for DeepSeek-R1-Distill-7B (Reviewer B)"""
    
    def __init__(self):
        super().__init__(
            model_name="DeepSeek-7B",
            endpoint_url=settings.deepseek_7b_url
        )


# Factory function
def get_local_model_runner(model_type: str) -> LocalModelRunner:
    """Get appropriate model runner"""
    runners = {
        "llama7b": Llama7BRunner,
        "gptj6b": GPTJ6BRunner,
        "mistral7b": Mistral7BRunner,
        "deepseek7b": DeepSeek7BRunner
    }
    
    runner_class = runners.get(model_type.lower())
    if not runner_class:
        raise ValueError(f"Unknown model type: {model_type}")
    
    return runner_class()
