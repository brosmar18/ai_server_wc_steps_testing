"""
FastAPI application setup and configuration.

This module contains:
- FastAPI app initialization
- Lifespan event handlers
- Router registration
- Core endpoints
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging_config import setup_logging, get_logger
from app.core.config import config
from app.api.routers import objects, upload

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown events.
    Code before yield runs on startup.
    Code after yield runs on shutdown.
    """
    # Startup
    logger.info("Application startup complete")
    logger.info(f"Connected to CDATA API at: {config.CDATA_API_BASE}")
    yield
    # Shutdown
    logger.info("Application shutting down")


# Create FastAPI app
app = FastAPI(
    title="CSV Import AI Assistant",
    description="AI-powered CSV import mapping for CDATA",
    version="1.0.0",
    lifespan=lifespan
)

logger.info("FastAPI application initialized")

# CORS Middleware to allow access from frontend app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

logger.info("CORS middleware configured")


# Include routers
app.include_router(objects.router)
app.include_router(upload.router)

logger.info("API routers registered")


@app.get("/")
async def root():
    """
    Health check endpoint.
    
    Returns basic application status and configuration info.
    """
    logger.info("Health check endpoint called")
    return {
        "status": "ok",
        "message": "CSV Import AI Assistant is running",
        "api_configured": bool(config.CDATA_API_BASE)
    }