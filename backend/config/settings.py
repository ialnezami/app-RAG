"""
Application settings and configuration.
"""
import os
from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = Field(default="RAG Application", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="BACKEND_PORT")
    reload: bool = Field(default=False, env="RELOAD")
    
    # Database
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_db: str = Field(default="rag_db", env="POSTGRES_DB")
    postgres_user: str = Field(default="rag_user", env="POSTGRES_USER")
    postgres_password: str = Field(default="secure_password", env="POSTGRES_PASSWORD")
    
    # API Keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )
    
    # File Upload
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    allowed_file_types: List[str] = Field(
        default=["pdf", "docx", "txt", "md"],
        env="ALLOWED_FILE_TYPES"
    )
    upload_dir: str = Field(default="uploads", env="UPLOAD_DIR")
    
    # Authentication
    enable_auth: bool = Field(default=False, env="ENABLE_AUTH")
    token_expire_hours: int = Field(default=24, env="TOKEN_EXPIRE_HOURS")
    
    # AI Settings
    default_embedding_provider: str = Field(default="openai", env="DEFAULT_EMBEDDING_PROVIDER")
    default_embedding_model: str = Field(default="text-embedding-3-small", env="DEFAULT_EMBEDDING_MODEL")
    embedding_dimensions: int = Field(default=1536, env="EMBEDDING_DIMENSIONS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Features
    enable_auth: bool = Field(default=False, env="ENABLE_AUTH")
    enable_rate_limiting: bool = Field(default=True, env="ENABLE_RATE_LIMITING")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000"]
    
    @validator("allowed_file_types", pre=True)
    def parse_allowed_file_types(cls, v):
        """Parse allowed file types from string or list."""
        if isinstance(v, str):
            return [ft.strip() for ft in v.split(",")]
        return v
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment setting."""
        if v not in ["development", "staging", "production"]:
            raise ValueError("Environment must be development, staging, or production")
        return v
    
    @property
    def database_url(self) -> str:
        """Get database URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@"
            f"{self.postgres_host}:"
            f"{self.postgres_port}/"
            f"{self.postgres_db}"
        )
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Convenience function for dependency injection
def get_settings_dependency() -> Settings:
    """Get settings for dependency injection."""
    return get_settings()
