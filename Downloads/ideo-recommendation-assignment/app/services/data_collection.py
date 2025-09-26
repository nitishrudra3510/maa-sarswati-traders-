"""
External API integration service for Video Recommendation Engine.
Handles data collection from Socialverse APIs with proper authentication and caching.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from cachetools import TTLCache

from app.config import settings

logger = logging.getLogger(__name__)

# Cache configuration - 5 minutes TTL for API responses
api_cache = TTLCache(maxsize=1000, ttl=300)


class ExternalAPIService:
    """Service for interacting with external Socialverse APIs."""
    
    def __init__(self):
        self.base_url = settings.API_BASE_URL
        self.flic_token = settings.FLIC_TOKEN
        self.resonance_algorithm = settings.RESONANCE_ALGORITHM
        self.timeout = httpx.Timeout(30.0)
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Accept": "application/json",
            "Flic-Token": self.flic_token,
            "User-Agent": "Video-Recommendation-Engine/1.0"
        }
    
    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key for API request."""
        sorted_params = sorted(params.items()) if params else []
        param_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        return f"{endpoint}?{param_str}"
    
    async def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Make HTTP request to external API with caching and error handling."""
        
        if params is None:
            params = {}
            
        cache_key = self._get_cache_key(endpoint, params)
        
        # Check cache first
        if use_cache and cache_key in api_cache:
            logger.info(f"Cache hit for {cache_key}")
            return api_cache[cache_key]
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers=self._get_headers(),
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Cache successful response
                if use_cache:
                    api_cache[cache_key] = data
                    logger.info(f"Cached response for {cache_key}")
                
                return data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for {url}: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 401:
                raise ValueError("Invalid Flic-Token. Please check authentication.")
            elif e.response.status_code == 429:
                raise ValueError("Rate limit exceeded. Please try again later.")
            else:
                raise ValueError(f"API request failed with status {e.response.status_code}")
                
        except httpx.TimeoutException:
            logger.error(f"Timeout for {url}")
            raise ValueError("Request timeout. Please try again.")
            
        except httpx.RequestError as e:
            logger.error(f"Request error for {url}: {str(e)}")
            raise ValueError(f"Network error: {str(e)}")
    
    async def get_viewed_posts(
        self, 
        page: int = 1, 
        page_size: int = 1000
    ) -> Dict[str, Any]:
        """Fetch viewed posts from external API."""
        params = {
            "page": page,
            "page_size": page_size,
            "resonance_algorithm": self.resonance_algorithm
        }
        return await self._make_request("posts/view", params)
    
    async def get_liked_posts(
        self, 
        page: int = 1, 
        page_size: int = 1000
    ) -> Dict[str, Any]:
        """Fetch liked posts from external API."""
        params = {
            "page": page,
            "page_size": page_size,
            "resonance_algorithm": self.resonance_algorithm
        }
        return await self._make_request("posts/like", params)
    
    async def get_inspired_posts(
        self, 
        page: int = 1, 
        page_size: int = 1000
    ) -> Dict[str, Any]:
        """Fetch inspired posts from external API."""
        params = {
            "page": page,
            "page_size": page_size,
            "resonance_algorithm": self.resonance_algorithm
        }
        return await self._make_request("posts/inspire", params)
    
    async def get_rated_posts(
        self, 
        page: int = 1, 
        page_size: int = 1000
    ) -> Dict[str, Any]:
        """Fetch rated posts from external API."""
        params = {
            "page": page,
            "page_size": page_size,
            "resonance_algorithm": self.resonance_algorithm
        }
        return await self._make_request("posts/rating", params)
    
    async def get_all_posts(
        self, 
        page: int = 1, 
        page_size: int = 1000
    ) -> Dict[str, Any]:
        """Fetch all posts summary from external API."""
        params = {
            "page": page,
            "page_size": page_size
        }
        return await self._make_request("posts/summary/get", params)
    
    async def get_all_users(
        self, 
        page: int = 1, 
        page_size: int = 1000
    ) -> Dict[str, Any]:
        """Fetch all users from external API."""
        params = {
            "page": page,
            "page_size": page_size
        }
        return await self._make_request("users/get_all", params)
    
    async def sync_data_to_database(self) -> Dict[str, int]:
        """Sync external API data to local database."""
        # This would integrate with database operations
        # For now, return mock sync results
        return {
            "users_synced": 0,
            "videos_synced": 0,
            "engagements_synced": 0
        }


# Global service instance
external_api_service = ExternalAPIService()
