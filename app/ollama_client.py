import requests
import os
import json

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

def generate_response(prompt: str, model: str = "llama3.1:8b") -> str:
    """
    Sends a prompt to the Ollama API and returns the response.
    """
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        return ""
