import requests

def test_cache_and_language():
    base_url = "http://localhost:8000"
    
    # Test 1: Ask a question in Chinese
    print("=== Test 1: Chinese Question ===")
    response = requests.post(f"{base_url}/ask", json={"question": "有多少個客戶？", "summary": True})
    print(f"Response: {response.json()['answer']}\n")
    
    # Test 2: Ask a question in English
    print("=== Test 2: English Question ===")
    response = requests.post(f"{base_url}/ask", json={"question": "How many customers are there?", "summary": True})
    print(f"Response: {response.json()['answer']}\n")
    
    # Test 3: Clear cache
    print("=== Test 3: Clear Cache ===")
    response = requests.post(f"{base_url}/clear-cache")
    print(f"Response: {response.json()}\n")
    
    # Test 4: Ask the same Chinese question again (should regenerate SQL)
    print("=== Test 4: Chinese Question After Cache Clear ===")
    response = requests.post(f"{base_url}/ask", json={"question": "有多少個客戶？", "summary": True})
    print(f"Response: {response.json()['answer']}\n")

if __name__ == "__main__":
    test_cache_and_language()
