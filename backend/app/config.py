from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Growth Co-pilot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://growthcopilot.ai"]
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost/growthcopilot"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600  # 1 hour default
    COMPETITOR_CACHE_TTL: int = 86400  # 24 hours
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # API Keys - AI Providers (Claude is preferred if both are set)
    CLAUDE_API_KEY: str = ""  # Anthropic Claude API
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"  # Latest Claude 3.5 Sonnet
    
    OPENAI_API_KEY: str = ""  # OpenAI API
    OPENAI_MODEL: str = "gpt-4o"  # Latest GPT-4o model (better than gpt-4-turbo)
    
    GOOGLE_PAGESPEED_API_KEY: str = ""
    SIMILARWEB_API_KEY: str = ""  # SimilarWeb API for traffic data
    
    # Google OAuth Settings for GA4 Integration
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    
    # Urlbox Screenshot API
    URLBOX_API_KEY: str = ""
    URLBOX_API_SECRET: str = ""
    
    # Legacy (deprecated)
    SCREENLY_API_KEY: str = ""
    BUILTWITH_API_KEY: str = ""
    
    # Security
    SECRET_KEY: str = "change-this-in-production"
    SHARE_SLUG_LENGTH: int = 8
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Analysis Settings
    ANALYSIS_TIMEOUT: int = 60  # seconds
    MAX_CONCURRENT_ANALYSES: int = 10
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Feature Flags
    ENABLE_SLACK_INTEGRATION: bool = False
    ENABLE_PAYMENT: bool = False
    ENABLE_AUTH: bool = False
    ENABLE_SCREENSHOTS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()