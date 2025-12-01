"""
Caching layer for pipeline responses
"""

import hashlib
import json
import os
from typing import Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from diskcache import Cache
from app.config import settings
from app.utils.logger import logger


class ResponseCache:
    """Cache manager for pipeline responses"""
    
    def __init__(self):
        self.enabled = settings.enable_cache
        self.ttl = settings.cache_ttl
        
        # Initialize disk cache
        cache_dir = Path(settings.cache_dir)
        cache_dir.mkdir(exist_ok=True)
        
        self.cache = Cache(str(cache_dir))
        
        logger.info(f"Cache initialized: enabled={self.enabled}, ttl={self.ttl}s")
    
    def _generate_key(self, query: str, options: dict = None) -> str:
        """Generate cache key from query and options"""
        # Create a deterministic key
        cache_input = {
            "query": query.strip().lower(),
            "options": options or {}
        }
        
        # Hash the input
        key_string = json.dumps(cache_input, sort_keys=True)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        
        return f"query:{key_hash}"
    
    def get(self, query: str, options: dict = None) -> Optional[dict]:
        """
        Get cached response
        
        Returns:
            Cached response dict or None if not found
        """
        if not self.enabled:
            return None
        
        try:
            key = self._generate_key(query, options)
            cached = self.cache.get(key)
            
            if cached:
                logger.debug(f"Cache HIT for query: {query[:50]}...")
                return cached
            else:
                logger.debug(f"Cache MISS for query: {query[:50]}...")
                return None
                
        except Exception as e:
            logger.warning(f"Cache get failed: {str(e)}")
            return None
    
    def set(self, query: str, response: dict, options: dict = None):
        """
        Cache a response
        
        Args:
            query: User query
            response: Pipeline response to cache
            options: Query options
        """
        if not self.enabled:
            return
        
        try:
            key = self._generate_key(query, options)
            
            # Add cache metadata
            response['metadata']['cache_hit'] = False
            response['metadata']['cached_at'] = datetime.utcnow().isoformat()
            
            self.cache.set(key, response, expire=self.ttl)
            logger.debug(f"Cached response for query: {query[:50]}...")
            
        except Exception as e:
            logger.warning(f"Cache set failed: {str(e)}")
    
    def clear(self):
        """Clear all cached responses"""
        try:
            self.cache.clear()
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Cache clear failed: {str(e)}")
            raise
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        try:
            return {
                "size": len(self.cache),
                "enabled": self.enabled,
                "ttl": self.ttl,
                "directory": settings.cache_dir
            }
        except Exception as e:
            logger.warning(f"Failed to get cache stats: {str(e)}")
            return {}
    
    def delete(self, query: str, options: dict = None):
        """Delete a specific cached response"""
        try:
            key = self._generate_key(query, options)
            self.cache.delete(key)
            logger.debug(f"Deleted cache for query: {query[:50]}...")
        except Exception as e:
            logger.warning(f"Cache delete failed: {str(e)}")


# Global cache instance
_cache_instance = None


def get_cache() -> ResponseCache:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = ResponseCache()
    return _cache_instance
