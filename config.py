"""Application configuration management"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Application configuration from environment variables"""
    
    # MongoDB settings
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "your_database")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "users")
    
    # API settings
    API_BASE_URL = os.getenv("API_BASE_URL", "https://api.example.com")
    API_KEY = os.getenv("API_KEY", "your_api_key")
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    
    # Performance settings
    CONCURRENT_REQUESTS = int(os.getenv("CONCURRENT_REQUESTS", "20"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.1"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_vars = {
            "MONGO_URI": cls.MONGO_URI,
            "DB_NAME": cls.DB_NAME,
            "COLLECTION_NAME": cls.COLLECTION_NAME,
            "API_BASE_URL": cls.API_BASE_URL,
            "API_KEY": cls.API_KEY
        }
        
        missing = [key for key, value in required_vars.items() 
                   if not value or value.startswith("your_")]
        
        if missing:
            raise ValueError(
                f"Missing or invalid required environment variables: {', '.join(missing)}"
            )
        
        logger.info("Configuration validated successfully")

