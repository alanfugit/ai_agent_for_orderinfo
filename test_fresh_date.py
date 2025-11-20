import requests

def test_fresh_date_query():
    url = "http://localhost:8000/ask"
    question = "過去30天的訂單總金額是多少？"  # Slightly different wording
    
    print(f"Question: {question}")
    response = requests.post(url, json={"question": question, "summary": True})
    result = response.json()
    print(f"Response: {result['answer']}")

if __name__ == "__main__":
    test_fresh_date_query()
