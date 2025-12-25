from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import ingest, chat, history
from src.config.settings import settings


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="RAG Chatbot API for Physical AI & Humanoid Robotics Book"
    )

    # Add CORS middleware - only allow Vercel domain
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://physical-ai-humanoid-robotics-textb-six.vercel.app",  # Production Vercel URL
            "http://localhost:3000",  # Local development
            "http://localhost:3001",  # Alternative local development
            "http://localhost:8080"   # Alternative local development
        ],
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
