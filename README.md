## App to Sync User Information



## **File Breakdown:**

1. **config.py** - Centralized configuration with validation
2. **models.py** - Data classes and type definitions
3. **database.py** - All MongoDB operations isolated
4. **api_client.py** - External API communication with retry logic
5. **sync_service.py** - Core synchronization business logic
6. **main.py** - Entry point that orchestrates everything

user_sync_app/
├── config.py          # Configuration management
├── models.py          # Data models (UserUpdate)
├── database.py        # MongoDB operations
├── api_client.py      # External API client
├── sync_service.py    # Business logic for syncing
├── logger.py # Define Custom Logger
├── main.py            # Application entry point
├── .env               # Environment variables
├── .env.example       # Example environment file
└── requirements.txt   # Dependencies





How to Run:

```python
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your actual values

# Run the application
python main.py
```
