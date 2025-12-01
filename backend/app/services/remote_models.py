"""
Remote model API clients
Handles Hugging Face and Gemini API calls
"""

import httpx
import json
from typing import Dict, Any
import google.generativeai as genai
from app.config import settings
from app.utils.logger import logger
from app.utils.error_handler import ModelAPIError, ModelTimeoutError


class HuggingFaceClient:
    """Client for Hugging Face Inference API"""
    
    def __init__(self):
        self.model = settings.huggingface_model
        self.api_url = f"{settings.huggingface_api_url}/{self.model}"
        self.api_token = settings.huggingface_api_token
        self.timeout = settings.request_timeout
        
        if not self.api_token:
            logger.warning("Hugging Face API token not set!")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        self.client = httpx.AsyncClient(timeout=self.timeout)
    
    async def generate(self, prompt_config: dict) -> str:
        """
        Generate response from Hugging Face model
        
        Args:
            prompt_config: Dict with 'inputs' and 'parameters'
            
        Returns:
            Generated text
        """
        try:
            logger.debug(f"Calling Hugging Face model: {self.model}")
            
            response = await self.client.post(
                self.api_url,
                headers=self.headers,
                json=prompt_config
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
            elif isinstance(result, dict):
                generated_text = result.get("generated_text", result.get("text", ""))
            else:
                generated_text = str(result)
            
            # Remove input prompt if included in response
            if "inputs" in prompt_config:
                generated_text = generated_text.replace(prompt_config["inputs"], "").strip()
            
            logger.debug(f"HF response: {generated_text[:100]}...")
            return generated_text
            
        except httpx.TimeoutException as e:
            logger.error(f"Hugging Face timeout: {str(e)}")
            raise ModelTimeoutError("Hugging Face API request timed out")
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Hugging Face HTTP error: {e.response.status_code}")
            error_detail = e.response.text
            raise ModelAPIError(f"Hugging Face API error: {error_detail}")
            
        except Exception as e:
            logger.error(f"Hugging Face error: {str(e)}")
            raise ModelAPIError(f"Hugging Face call failed: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check if HF API is accessible"""
        try:
            response = await self.client.get(
                self.api_url,
                headers=self.headers,
                timeout=10.0
            )
            return response.status_code in [200, 503]  # 503 = model loading
        except Exception:
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class GeminiClient:
    """Client for Google Gemini API"""
    
    def __init__(self):
        self.model_name = settings.gemini_model
        self.api_key = settings.gemini_api_key
        self.temperature = settings.gemini_temperature
        self.max_tokens = settings.gemini_max_tokens
        
        if not self.api_key:
            logger.warning("Gemini API key not set!")
        else:
            genai.configure(api_key=self.api_key)
        
        self.model = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Lazy initialization of model"""
        if not self._initialized and self.api_key:
            self.model = genai.GenerativeModel(self.model_name)
            self._initialized = True
    
    async def generate(self, prompt: str) -> str:
        """
        Generate response from Gemini
        
        Args:
            prompt: Text prompt
            
        Returns:
            Generated text
        """
        try:
            self._ensure_initialized()
            
            if not self.model:
                raise ModelAPIError("Gemini API not configured")
            
            logger.debug(f"Calling Gemini model: {self.model_name}")
            
            generation_config = genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                candidate_count=1
            )
            
            # Generate response (synchronous API)
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            generated_text = response.text
            
            logger.debug(f"Gemini response: {generated_text[:100]}...")
            return generated_text.strip()
            
        except Exception as e:
            logger.error(f"Gemini error: {str(e)}")
            raise ModelAPIError(f"Gemini call failed: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check if Gemini API is accessible"""
        try:
            if not self.api_key:
                return False
            
            self._ensure_initialized()
            
            # Simple test generation
            response = self.model.generate_content("Test")
            return bool(response.text)
            
        except Exception:
            return False


# Global instances
_hf_client = None
_gemini_client = None


def get_hf_client() -> HuggingFaceClient:
    """Get global HF client instance"""
    global _hf_client
    if _hf_client is None:
        _hf_client = HuggingFaceClient()
    return _hf_client


def get_gemini_client() -> GeminiClient:
    """Get global Gemini client instance"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
