import requests
import json
import sys

def test_api():
    url = "http://localhost:8002/ask"
    # A question that should be answerable from the schema provided
    question = "How many customers are there?"
    
    payload = {
        "question": question
    }
    
    print(f"Sending question: {question}")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"Answer: {data['answer']}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response content: {e.response.text}")
        return False

if __name__ == "__main__":
    if test_api():
        sys.exit(0)
    else:
        sys.exit(1)
