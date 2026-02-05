import requests
import json

# Test the chat endpoint with multiple queries
url = "http://127.0.0.1:8000/api/v1/chat"
headers = {
    "Content-Type": "application/json"
}

# Test 1: Basic greeting
print("=== Test 1: Basic greeting ===")
data = {
    "session_id": "test-session-123",
    "message": "Hello, are you working?"
}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()['response']}")
    print(f"Sources returned: {len(response.json()['sources'])}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Test 2: Question about AI ===")
data2 = {
    "session_id": "test-session-456",
    "message": "What is artificial intelligence?"
}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data2))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()['response']}")
    print(f"Sources returned: {len(response.json()['sources'])}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== Test 3: Question about humanoid robots ===")
data3 = {
    "session_id": "test-session-789",
    "message": "Tell me about humanoid robots"
}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data3))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()['response']}")
    print(f"Sources returned: {len(response.json()['sources'])}")
except Exception as e:
    print(f"Error: {e}")