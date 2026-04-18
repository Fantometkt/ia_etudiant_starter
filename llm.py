import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "gemma3"

def build_request_payload(messages, temp=0.3):
    return {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temp}
    }

def call_ollama(messages, temp=0.3):
    try:
        r = requests.post(OLLAMA_URL, json=build_request_payload(messages, temp))
        r.raise_for_status()
        return r.json().get("message", {}).get("content", "").strip()
    except Exception as e:
        return f"Erreur IA : {str(e)}"