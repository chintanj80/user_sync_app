"""Database management module"""

import logging
from typing import List, Dict, Any, Optional

from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError

from models import UserUpdate
from config import Config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MongoDB connections and operations using native async PyMongo"""
    
    def __init__(self, uri: str, db_name: str, collection_name: str):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client: Optional[AsyncMongoClient] = None
        self.collection = None
    
    async def connect(self):
        """Establish database connection"""
        try:
            self.client = AsyncMongoClient(self.uri)
            # Verify connection
            await self.client.admin.command('ping')
            self.collection = self.client[self.db_name][self.collection_name]
            logger.info("Successfully connected to MongoDB")
        except PyMongoError as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Fetch all users from the collection"""
        try:
            cursor = self.collection.find(
                {}, 
                {"_id": 1, "user_id": 1, "phone_number": 1, "city": 1, "state": 1}
            )
            users = await cursor.to_list(length=None)
            logger.info(f"Retrieved {len(users)} users from database")
            return users
        except PyMongoError as e:
            logger.error(f"Error fetching users: {e}")
            raise
    
    async def bulk_update_users(self, updates: List[UserUpdate]) -> int:
        """Perform bulk updates on user records"""
        if not updates:
            return 0
        
        operations = []
        for update in updates:
            update_doc = {
                "$set": {
                    "last_synced": update.last_synced
                }
            }
            
            if update.phone_number is not None:
                update_doc["$set"]["phone_number"] = update.phone_number
            if update.city is not None:
                update_doc["$set"]["city"] = update.city
            if update.state is not None:
                update_doc["$set"]["state"] = update.state
            
            operations.append({
                "update_one": {
                    "filter": {"user_id": update.user_id},
                    "update": update_doc,
                    "upsert": False
                }
            })
        
        try:
            # Process in batches to avoid memory issues
            total_modified = 0
            batch_size = Config.BATCH_SIZE
            
            for i in range(0, len(operations), batch_size):
                batch = operations[i:i + batch_size]
                result = await self.collection.bulk_write(batch, ordered=False)
                total_modified += result.modified_count
                logger.debug(f"Processed batch {i//batch_size + 1}: "
                           f"{result.modified_count} modified")
            
            logger.info(f"Updated {total_modified} user records")
            return total_modified
        except PyMongoError as e:
            logger.error(f"Error performing bulk update: {e}")
            raise