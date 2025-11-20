import requests

def test_formatting():
    url = "http://localhost:8000/ask"
    question = "那個產品最多人買" # Which product is bought by the most people?
    
    print(f"--- Test with summary=False ---")
    response = requests.post(url, json={"question": question, "summary": False})
    print(f"Response: {response.json()['answer']}")
    
    print(f"\n--- Test with summary=True ---")
    response = requests.post(url, json={"question": question, "summary": True})
    print(f"Response: {response.json()['answer']}")

if __name__ == "__main__":
    test_formatting()
