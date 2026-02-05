import requests
import json

# Test the frontend-backend integration
print("Testing frontend-backend integration...")

# Test the backend directly first
print("\n1. Testing backend connection...")
try:
    response = requests.get("http://127.0.0.1:8000/")
    print(f"   Backend status: {response.status_code}")
    print(f"   Backend response: {response.json()}")
except Exception as e:
    print(f"   Backend error: {e}")

# Test the chat endpoint
print("\n2. Testing chat endpoint...")
try:
    chat_data = {
        "session_id": "integration-test",
        "message": "Hello, this is a test message"
    }
    response = requests.post(
        "http://127.0.0.1:8000/api/v1/chat",
        headers={"Content-Type": "application/json"},
        data=json.dumps(chat_data)
    )
    print(f"   Chat endpoint status: {response.status_code}")
    if response.status_code == 200:
        response_data = response.json()
        print(f"   Response length: {len(response_data['response'])} chars")
        print(f"   Sources returned: {len(response_data['sources'])}")
    else:
        print(f"   Chat endpoint error response: {response.text}")
except Exception as e:
    print(f"   Chat endpoint error: {e}")

print("\n3. Frontend should be accessible at: http://localhost:3000")
print("4. Chatbot page should be accessible at: http://localhost:3000/chatbot")
print("\nIntegration test completed!")