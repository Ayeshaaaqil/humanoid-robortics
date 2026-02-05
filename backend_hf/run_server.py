import sys
import os
import threading
import time
import requests

# Add the current directory to the path
sys.path.insert(0, os.path.abspath('.'))

# Import the app
from src.api.main import app
import uvicorn

def run_server():
    """Run the server in a separate thread"""
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8080,
        log_level="info"
    )
    server = uvicorn.Server(config)
    server.run()

def test_server():
    """Start the server and test it"""
    print("Starting the RAG Chatbot API server...")
    print("This may take a moment as models are loaded...")
    
    # Start server in a thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait a moment for the server to start
    time.sleep(3)
    
    # Test if the server is running
    try:
        response = requests.get("http://127.0.0.1:8080/", timeout=5)
        if response.status_code == 200:
            print("✓ Server is running successfully!")
            print("✓ Access the API at: http://127.0.0.1:8080")
            print("✓ API documentation: http://127.0.0.1:8080/docs")
            print("✓ Chat endpoint: http://127.0.0.1:8080/api/v1/chat")
            return True
        else:
            print(f"✗ Server responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Server is not responding. There may be an issue with the startup.")
        return False
    except Exception as e:
        print(f"✗ Error testing server: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    
    if success:
        print("\nYour RAG chatbot API is now running and ready to use!")
        print("You can now connect your frontend to this backend.")
    else:
        print("\nThere was an issue starting the server.")
        print("Please check that:")
        print("- Your environment variables are set correctly")
        print("- Ports 8080 is not used by another application")
        print("- All required packages are installed")
    
    # Keep the main thread alive so the server continues running
    print("\nServer is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")