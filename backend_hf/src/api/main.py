from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.api.routes import ingest, chat, history
from src.config.settings import settings
from src.services.database_service import init_db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    yield
    # Shutdown: (Cleanup if needed)
    logger.info("Shutting down...")

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="RAG Chatbot API for Physical AI & Humanoid Robotics Book",
        lifespan=lifespan
    )

    # Add CORS middleware
    origins = settings.ALLOWED_ORIGINS
    logger.info(f"Configuring CORS with origins: {origins}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(ingest.router, prefix=settings.API_V1_STR)
    app.include_router(chat.router, prefix=settings.API_V1_STR)
    app.include_router(history.router, prefix=settings.API_V1_STR)

    @app.get("/")
    def read_root():
        return {
            "message": "RAG Chatbot API",
            "version": settings.VERSION,
            "status": "running"
        }

    return app


# Create the application instance
app = create_app()


# For running with uvicorn directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Only in development
    )