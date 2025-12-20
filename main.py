from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.logging_config import setup_logging, get_logger
from app.core.config import config

setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lifespan event handler for startup and shutdown events.

    logger.info("Application startup complete")
    yield
    logger.info("Application shutting down")

    """
        @asynccontextmanager turns function into an async context manager. 
        FastAPI uses the context manager to control the entire lifetime of the app. 
        Code before yield -> Runs on startup. 
        Code after yield -> Runs on shutdown. 
        The yield -> Hands control to FastAPI and keeps the app alive. 

    """
app = FastAPI(
    title="AI Server"
)

logger.info("FastAPI app initialized")

@app.get("/")
async def root():
    # Health check endpoint
    logger.info("Health check endpoint called!")
    return {
        "status": "OK",
        "message": "AI Server is Running!",
        "api_configured": bool(config.CDATA_API_BASE)
    }