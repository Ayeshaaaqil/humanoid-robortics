import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    # Gemini settings (currently not used, but kept for future use)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Cohere settings
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    
    # Qdrant settings
    QDRANT_CLIENT_URL: str = os.getenv("QDRANT_CLIENT_URL", "http://localhost:6333")
    QDRANT_CLIENT_API_KEY: str = os.getenv("QDRANT_CLIENT_API_KEY", "")
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    
    # Application settings
    APP_NAME: str = "RAG Chatbot API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        origins = os.getenv("ALLOWED_ORIGINS", "*")
        return [origin.strip() for origin in origins.split(",")]

# Create a singleton instance
settings = Settings()