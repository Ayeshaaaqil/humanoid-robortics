import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Set environment variables for settings
import dotenv
dotenv.load_dotenv()

from src.api.main import app
import uvicorn

if __name__ == "__main__":
    print("Starting RAG Chatbot API Server...")
    print("Loading services and initializing models...")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload for production
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()