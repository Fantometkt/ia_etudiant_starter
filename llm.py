import os
import requests

LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama").strip().lower()

# Backend Ollama
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3")

# Backend vLLM (OpenAI-compatible server)
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
VLLM_MODEL = os.getenv("VLLM_MODEL", OLLAMA_MODEL)
VLLM_API_KEY = os.getenv("VLLM_API_KEY", "local-dev-token")

REQUEST_TIMEOUT = float(os.getenv("LLM_REQUEST_TIMEOUT", "180"))

def _build_ollama_payload(messages, temp=0.3):
    return {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temp},
    }

def _call_ollama(messages, temp=0.3):
    r = requests.post(
        OLLAMA_URL,
        json=_build_ollama_payload(messages, temp),
        timeout=REQUEST_TIMEOUT,
    )
    r.raise_for_status()
    return r.json().get("message", {}).get("content", "").strip()

def _build_vllm_payload(messages, temp=0.3):
    return {
        "model": VLLM_MODEL,
        "messages": messages,
        "temperature": temp,
        "stream": False,
    }

def _call_vllm(messages, temp=0.3):
    url = f"{VLLM_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {VLLM_API_KEY}",
        "Content-Type": "application/json",
    }
    r = requests.post(
        url,
        headers=headers,
        json=_build_vllm_payload(messages, temp),
        timeout=REQUEST_TIMEOUT,
    )
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()

def call_llm(messages, temp=0.3):
    try:
        if LLM_BACKEND == "ollama":
            return _call_ollama(messages, temp=temp)
        if LLM_BACKEND == "vllm":
            return _call_vllm(messages, temp=temp)
        return f"Erreur IA : backend inconnu '{LLM_BACKEND}'"
    except Exception as e:
        return f"Erreur IA : {str(e)}"

# Compatibilité avec le reste du projet
def call_ollama(messages, temp=0.3):
    return call_llm(messages, temp=temp)