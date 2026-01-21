"""
Configuration Manangement
Uses Pydantic for type-safe settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # Project Info
    PROJECT_NAME: str = "Priyank's - Portfolio"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str= "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./portfolio.db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8080",
        "http://localhost:3000",
        "https://priyankrao.co"
    ]

    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    WEBHOOK_URL: str= ""

    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_UPLOAD_SIZE_MB: int = 30

    ENABLES_ANALYTICS: bool = False
    TRACK_RESPONSE_TIME: bool = True

    IGNORE_COMPANIES: str= ""
    IGNORE_NAMES: str = ""

    RATE_LIMIT_PER_MINUTE: int = 60

    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".txt", ".md"]
    UPLOAD_DIR: str= "./uploads"

    LOG_LEVEL: str= "INFO"

    class config:
        env_file= ".env"
        env_file_encoding = "utf-8"
        case_sensitive=True

    @property
    def is_producion(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == "development"
    
    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins based on environment"""
        if self.is_producion:
            return ["https://priyankrao.co"]
        return self.ALLOWED_ORIGINS
    
    @property
    def database_type(self) -> str:
        """Get database type from URL"""

        if "postresql" in self.DATABASE_URL:
            return "postresql"
        elif "sqlite" in self.DATABASE_URL:
            return "sqlite"
        return "unknown"
    
    @property
    def ignored_companies(self)-> List[str]:
        """Parse ignore companies from comma-seperated string"""
        if not self.IGNORE_COMPANIES:
            return []
        return [c.strip() for c in self.IGNORE_COMPANIES.split(",")]
    
    @property
    def ignored_name(self) -> List[str]:
        """Parse ignored names from comma-seperated string"""
        if not self.IGNORE_NAMES:
            return []
        return [c.strip() for c in self.IGNORE_NAMES.split(",")]
    
    def validate_production_settings(self):
        """Validate critical settings for production"""
        if not self.is_producion:
            return
        
        errors = []

        if self.SECRET_KEY == "your-secret-key-change-in-production-min-32-chars":
            errors.append("SECRET_KEY must be changed in produciton")
        if len(self.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be at least 32 characters!")
        if not self.OPENAI_API_KEY:
            errors.append("OPEN_API_KEY is required in production!")
        if self.DEBUG:
            errors.append("DEBUG must be False in production!")

        if "sqlite" in self.DATABASE_URL:
            print("⚠️ Warning: Using SQLite in production is not recommended!")

        if errors:
            raise ValueError(f"Production configuration erros: \n" + "\n".join(f"- {e}" for e in errors))
        
    def get_upload_path(self, filename: str) -> str:
        """Get full upload path for a file"""

        return os.path.join(self.UPLOAD_DIR, filename)
    
settings = Settings()

if settings.is_producion:
    settings.validate_production_settings()

if settings.is_development:
    if not settings.OPENAI_API_KEY:
        print("⚠️ Warning: OPENAI_API_KEY not set (chatbot won't work)")
    if not settings.GROQ_API_KEY:
        print("⚠️ Warning: GROQ_API_KEY not set (if using Groq)")
    if not settings.WEBHOOK_URL:
        print("⚠️ Warning: WEBHOOK_URL not set (contact form webhook disabled)")
    