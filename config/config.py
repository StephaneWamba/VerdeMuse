import os
from pydantic import BaseSettings
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings that can be configured via environment variables
    or secret files mounted in a container environment.
    """
    # App Settings
    APP_NAME: str = "VerdeMuse"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # API Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # LLM Settings
    MISTRAL_API_KEY: Optional[str] = os.getenv("MISTRAL_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Vector DB Settings
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./data/embeddings")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        case_sensitive = True

# Create settings object to be imported elsewhere in the app
settings = Settings()

# Environment-specific settings
def get_settings():
    """
    Returns the appropriate settings based on the environment.
    This can be used as a FastAPI dependency.
    """
    return settings