import os
from dotenv import load_dotenv

# Search and load key-value pairs from local .env environment file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Ghost Failure Detective Engine"
    API_V1_STR: str = "/api/v1"
    
    # GitHub Authentication Token (Required to bypass low rate-limits when downloading log archives)
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    
    # Simple SQLite local storage string for tracking flakiness metrics history
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ghost_telemetry.db")

settings = Settings()