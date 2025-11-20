import requests

def test_product_only():
    url = "http://localhost:8000/ask"
    question = "那個產品最多人買"
    
    print(f"Question: {question}")
    response = requests.post(url, json={"question": question, "summary": True})
    result = response.json()
    print(f"Response: {result['answer']}")

if __name__ == "__main__":
    test_product_only()
