import requests
import json

# Base URL for the Flask API
BASE_URL = "http://localhost:5000/api"

def test_health_check():
    """Test the health check endpoint"""
    print("=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_list_documents():
    """Test the list documents endpoint"""
    print("=== Testing List Documents ===")
    try:
        response = requests.get(f"{BASE_URL}/documents")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_ask_question(question):
    """Test the ask question endpoint"""
    print(f"=== Testing Ask Question: '{question}' ===")
    try:
        data = {"question": question}
        response = requests.post(f"{BASE_URL}/ask", json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_upload_document(file_path):
    """Test the upload document endpoint"""
    print(f"=== Testing Upload Document: {file_path} ===")
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(f"{BASE_URL}/upload", files=files)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    print()

if __name__ == "__main__":
    print("Flask RAG API Test Script")
    print("=" * 50)
    
    # Test health check
    test_health_check()
    
    # Test list documents
    test_list_documents()
    
    # Test ask question (only if vector store exists)
    test_ask_question("What is the main theme of the story?")
    
    # Uncomment the line below to test document upload
    # test_upload_document("path/to/your/document.txt")
    
    print("Test completed!") 