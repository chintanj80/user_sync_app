"""User synchronization service module"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from models import UserUpdate
from database import DatabaseManager
from api_client import ExternalAPIClient
from config import Config

logger = logging.getLogger(__name__)


class UserSyncService:
    """Orchestrates the user synchronization process"""
    
    def __init__(self, db_manager: DatabaseManager, api_client: ExternalAPIClient):
        self.db_manager = db_manager
        self.api_client = api_client
        self.semaphore = asyncio.Semaphore(Config.CONCURRENT_REQUESTS)
    
    async def fetch_and_prepare_update(self, user: Dict[str, Any]) -> Optional[UserUpdate]:
        """
        Fetch user data from API and prepare update object
        
        Args:
            user: User document from MongoDB
            
        Returns:
            UserUpdate object if changes detected, None otherwise
        """
        async with self.semaphore:
            user_id = user.get("user_id") or str(user.get("_id"))
            
            # Rate limiting
            await asyncio.sleep(Config.REQUEST_DELAY)
            
            try:
                api_data = await self.api_client.get_user_info(user_id)
                
                if not api_data:
                    return None
                
                # Check if any fields have changed
                current_phone = user.get("phone_number")
                current_city = user.get("city")
                current_state = user.get("state")
                
                api_phone = api_data.get("phone_number")
                api_city = api_data.get("city")
                api_state = api_data.get("state")
                
                if (current_phone != api_phone or 
                    current_city != api_city or 
                    current_state != api_state):
                    
                    logger.debug(f"Changes detected for user {user_id}")
                    return UserUpdate(
                        user_id=user_id,
                        phone_number=api_phone,
                        city=api_city,
                        state=api_state,
                        last_synced=datetime.utcnow()
                    )
                
                return None
                
            except Exception as e:
                logger.error(f"Error processing user {user_id}: {e}")
                return None
    
    async def sync_users(self) -> Dict[str, Any]:
        """
        Main synchronization method
        
        Returns:
            Dictionary with sync statistics
        """
        start_time = datetime.utcnow()
        logger.info("Starting user synchronization")
        
        try:
            # Fetch all users
            users = await self.db_manager.get_all_users()
            total_users = len(users)
            
            # Process users concurrently
            tasks = [self.fetch_and_prepare_update(user) for user in users]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out None values and exceptions
            updates = [
                result for result in results 
                if isinstance(result, UserUpdate)
            ]
            
            # Perform bulk update
            modified_count = 0
            if updates:
                modified_count = await self.db_manager.bulk_update_users(updates)
            
            # Calculate statistics
            duration = (datetime.utcnow() - start_time).total_seconds()
            errors_count = len([r for r in results if isinstance(r, Exception)])
            
            stats = {
                "total_users": total_users,
                "users_checked": len([r for r in results if not isinstance(r, Exception)]),
                "users_updated": modified_count,
                "errors": errors_count,
                "duration_seconds": duration
            }
            
            logger.info(f"Synchronization completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Synchronization failed: {e}")
            raise