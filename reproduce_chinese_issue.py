import requests
import json

def test_chinese_question():
    url = "http://localhost:8000/ask"
    question = "誰下單金額的总金额最多？"
    
    payload = {
        "question": question
    }
    
    print(f"Sending question: {question}")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"Answer: {data['answer']}")
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response content: {e.response.text}")

if __name__ == "__main__":
    test_chinese_question()
