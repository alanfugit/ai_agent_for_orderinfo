import requests

def test_date_query():
    url = "http://localhost:8000/ask"
    question = "最近一個月的訂單總額是多少"
    
    print(f"Question: {question}")
    response = requests.post(url, json={"question": question, "summary": True})
    result = response.json()
    print(f"Response: {result['answer']}")

if __name__ == "__main__":
    test_date_query()
