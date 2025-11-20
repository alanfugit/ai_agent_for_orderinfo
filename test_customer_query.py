import requests

def test_customer_query():
    url = "http://localhost:8000/ask"
    
    # Clear cache by asking a new question
    questions = [
        "哪個客戶的訂單總金額最高？前5名",  # Which customer has the highest total order amount? Top 5
        "那個產品最多人買",  # Which product is bought by the most people?
    ]
    
    for question in questions:
        print(f"\n--- Question: {question} ---")
        response = requests.post(url, json={"question": question, "summary": True})
        print(f"Response: {response.json()['answer']}")

if __name__ == "__main__":
    test_customer_query()
