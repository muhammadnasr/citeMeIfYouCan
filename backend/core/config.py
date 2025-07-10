from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str
    
    # Pinecone Configuration
    pinecone_api_key: str
    pinecone_environment: str = "us-east-1"
    pinecone_index: str = "journal-chunks"
    
    # API Configuration
    allowed_origins: List[str] = ["http://localhost:5173", "*"]
    
    # Additional application settings
    app_name: str = "Cite Me If You Can"
    debug: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

# Create a global settings instance
settings = Settings()
