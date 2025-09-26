"""
Configuration module for Video Recommendation Engine.
Handles environment variables and application settings.
"""

import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field


# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    FLIC_TOKEN: str = Field(default="", description="Flic-Token for external API authentication")
    API_BASE_URL: str = Field(
        default="https://api.socialverseapp.com",
        description="Base URL for external APIs"
    )
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/video_recommendation",
        description="PostgreSQL database connection URL"
    )
    
    # Redis Configuration (for caching)
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching"
    )
    
    # Application Configuration
    APP_NAME: str = Field(default="video-recommendation-engine", description="Application name")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # External API Configuration
    RESONANCE_ALGORITHM: str = Field(
        default="resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if",
        description="Resonance algorithm parameter for external APIs"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()