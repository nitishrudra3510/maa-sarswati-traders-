"""
Pydantic models for recommendation API responses.
Provides validation and serialization for API endpoints.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class VideoRecommendation(BaseModel):
    """Model for video recommendation response."""
    
    video_id: UUID = Field(..., description="Unique identifier for the video")
    title: str = Field(..., min_length=1, max_length=255, description="Video title")
    category: Optional[str] = Field(None, max_length=100, description="Video category")
    description: Optional[str] = Field(None, description="Video description")
    posted_at: datetime = Field(..., description="When the video was posted")
    recommendation_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Recommendation confidence score")
    recommendation_reason: str = Field(..., description="Why this video was recommended")
    
    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """Response model for recommendation endpoints."""
    
    recommendations: List[VideoRecommendation] = Field(..., description="List of video recommendations")
    total_count: int = Field(..., ge=0, description="Total number of recommendations")
    user_id: Optional[UUID] = Field(None, description="User ID for personalized recommendations")
    algorithm_used: str = Field(..., description="Algorithm used for recommendations")
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    version: str = Field(default="1.0.0", description="API version")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
