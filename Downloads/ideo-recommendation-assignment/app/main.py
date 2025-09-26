"""
Main FastAPI application for Video Recommendation Engine.
Configures the application with proper error handling, middleware, and API documentation.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.config import settings
from app.routes.recommendations import router as recommendations_router
from app.models.recommendation import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Video Recommendation Engine...")
    
    # Validate configuration
    if not settings.FLIC_TOKEN:
        logger.warning("FLIC_TOKEN not configured. External API calls will fail.")
    
    logger.info(f"API Base URL: {settings.API_BASE_URL}")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Video Recommendation Engine...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## Video Recommendation Engine
    
    A sophisticated recommendation system that suggests personalized video content 
    based on user preferences and engagement patterns using deep neural networks.
    
    ### Features
    - **Personalized Recommendations**: Collaborative filtering algorithm
    - **Cold Start Handling**: Mood-based recommendations inspired by Empowerverse App
    - **Category Filtering**: Project-specific video recommendations
    - **External API Integration**: Socialverse API data collection
    - **Caching**: Efficient response caching for performance
    
    ### Algorithms
    - **Current**: Collaborative Filtering with cosine similarity
    - **Future**: Deep Neural Networks for enhanced accuracy
    
    ### External APIs
    All external API calls require `Flic-Token` header for authentication.
    """,
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper error responses."""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=f"Request to {request.url.path} failed"
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with proper error responses."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail="An unexpected error occurred. Please try again later."
        ).dict()
    )


# Include routers
app.include_router(recommendations_router)


# Root endpoint
@app.get("/", response_model=Dict[str, Any])
async def root():
    """
    Root endpoint providing API information.
    """
    return {
        "message": "Video Recommendation Engine API",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs",
        "health_check": "/api/v1/health",
        "endpoints": {
            "personalized_feed": "/api/v1/feed?username={username}",
            "category_feed": "/api/v1/feed/category?username={username}&project_code={project_code}",
            "health_check": "/api/v1/health",
            "neural_suggestions": "/api/v1/neural-network-suggestions"
        }
    }


# Health check endpoint (additional to the one in router)
@app.get("/health", response_model=Dict[str, str])
async def health():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy"}


# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema with additional information."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom information
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )