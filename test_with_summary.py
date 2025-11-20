import requests

def test_with_summary():
    url = "http://localhost:8000/ask"
    question = "那個人買的產品總價最高？"
    
    print(f"Question: {question}")
    print("\n--- With summary=True ---")
    response = requests.post(url, json={"question": question, "summary": True})
    result = response.json()
    print(f"Response: {result['answer']}")
    
    print("\n--- With summary=False ---")
    response = requests.post(url, json={"question": question, "summary": False})
    result = response.json()
    print(f"Response: {result['answer']}")

if __name__ == "__main__":
    test_with_summary()
