"""External API client module"""

import asyncio
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

import aiohttp
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

logger = logging.getLogger(__name__)


class ExternalAPIClient:
    """Handles external API requests with retry logic"""
    
    def __init__(self, base_url: str, api_key: str, timeout: int):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
    
    @asynccontextmanager
    async def get_session(self):
        """Context manager for aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
        try:
            yield self.session
        finally:
            pass
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            logger.info("API client session closed")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch user information from external API with retry logic
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with user information or None if failed
        """
        async with self.get_session() as session:
            try:
                url = f"{self.base_url}/users/{user_id}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    elif response.status == 404:
                        logger.warning(f"User {user_id} not found in API")
                        return None
                    else:
                        logger.error(f"API error for user {user_id}: {response.status}")
                        response.raise_for_status()
            except aiohttp.ClientError as e:
                logger.error(f"API request failed for user {user_id}: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error for user {user_id}: {e}")
                return None