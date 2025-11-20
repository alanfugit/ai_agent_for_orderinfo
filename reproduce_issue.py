import requests
import json

def test_specific_question():
    url = "http://localhost:8000/ask"
    # The question that likely generated the problematic SQL
    question = "Who has the highest total order amount? List top 5."
    
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
    test_specific_question()
