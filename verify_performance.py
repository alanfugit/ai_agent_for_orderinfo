import requests
import time

def test_performance():
    url = "http://localhost:8000/ask"
    question = "How many customers are there?"
    
    print(f"--- Test 1: First call (Uncached, with summary) ---")
    start_time = time.time()
    response = requests.post(url, json={"question": question, "summary": True})
    end_time = time.time()
    print(f"Response: {response.json()['answer']}")
    print(f"Time: {end_time - start_time:.4f}s")
    
    print(f"\n--- Test 2: Second call (Cached SQL, with summary) ---")
    start_time = time.time()
    response = requests.post(url, json={"question": question, "summary": True})
    end_time = time.time()
    print(f"Response: {response.json()['answer']}")
    print(f"Time: {end_time - start_time:.4f}s")
    
    print(f"\n--- Test 3: Third call (Cached SQL, NO summary) ---")
    start_time = time.time()
    response = requests.post(url, json={"question": question, "summary": False})
    end_time = time.time()
    print(f"Response: {response.json()['answer']}")
    print(f"Time: {end_time - start_time:.4f}s")

if __name__ == "__main__":
    test_performance()
