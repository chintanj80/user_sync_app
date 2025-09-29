"""
MongoDB User Synchronization Application
Main entry point for the application
"""

import asyncio
import logging

from config import Config
from database import DatabaseManager
from api_client import ExternalAPIClient
from sync_service import UserSyncService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main application entry point"""
    try:
        # Validate configuration
        Config.validate()
        
        # Initialize components
        db_manager = DatabaseManager(
            uri=Config.MONGO_URI,
            db_name=Config.DB_NAME,
            collection_name=Config.COLLECTION_NAME
        )
        
        api_client = ExternalAPIClient(
            base_url=Config.API_BASE_URL,
            api_key=Config.API_KEY,
            timeout=Config.API_TIMEOUT
        )
        
        # Connect to database
        await db_manager.connect()
        
        # Create sync service
        sync_service = UserSyncService(db_manager, api_client)
        
        # Run synchronization
        stats = await sync_service.sync_users()
        
        # Print summary
        print(f"\n{'='*50}")
        print("Synchronization Summary")
        print(f"{'='*50}")
        print(f"Total Users: {stats['total_users']}")
        print(f"Users Checked: {stats['users_checked']}")
        print(f"Users Updated: {stats['users_updated']}")
        print(f"Errors: {stats['errors']}")
        print(f"Duration: {stats['duration_seconds']:.2f} seconds")
        print(f"{'='*50}\n")
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\nConfiguration Error: {e}")
        print("\nPlease ensure all required environment variables are set in your .env file")
        return
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise
    finally:
        # Cleanup
        await api_client.close()
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main())