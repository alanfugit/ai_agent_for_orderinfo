import requests

def test_error_query():
    url = "http://localhost:8000/ask"
    question = "那個人買的產品總價最高？"
    
    print(f"Question: {question}")
    response = requests.post(url, json={"question": question, "summary": False})
    result = response.json()
    print(f"Response: {result['answer']}")

if __name__ == "__main__":
    test_error_query()
