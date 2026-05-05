import os
import requests
from utils import env_float, env_int, clean

# =========================
# CONFIG
# =========================

LLM_BACKEND = os.getenv("LLM_BACKEND", "ollama").strip().lower()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3")

VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")
VLLM_MODEL = os.getenv("VLLM_MODEL", OLLAMA_MODEL)
VLLM_API_KEY = os.getenv("VLLM_API_KEY", "local-dev-token")

REQUEST_TIMEOUT = env_float("LLM_REQUEST_TIMEOUT", 180.0)
DEFAULT_MAX_TOKENS = env_int("LLM_DEFAULT_MAX_TOKENS", 1800)


# =========================
# NORMALISATION
# =========================

def _normalize_messages(messages):
    cleaned = []

    for m in messages or []:
        role = clean(m.get("role"))
        content = clean(m.get("content"))

        if not role or not content:
            continue

        if role not in {"system", "user", "assistant"}:
            role = "user"

        cleaned.append({
            "role": role,
            "content": content
        })

    return cleaned


# =========================
# PROVIDERS
# =========================

class OllamaProvider:
    def generate(self, messages, temp=0.3, max_tokens=None):
        options = {
            "temperature": float(temp),
        }

        if max_tokens:
            options["num_predict"] = int(max_tokens)

        payload = {
            "model": OLLAMA_MODEL,
            "messages": _normalize_messages(messages),
            "stream": False,
            "options": options,
        }

        r = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()

        return r.json().get("message", {}).get("content", "").strip()


class VLLMProvider:
    def generate(self, messages, temp=0.3, max_tokens=None):
        url = f"{VLLM_BASE_URL.rstrip('/')}/chat/completions"

        payload = {
            "model": VLLM_MODEL,
            "messages": _normalize_messages(messages),
            "temperature": float(temp),
            "stream": False,
            "max_tokens": int(max_tokens or DEFAULT_MAX_TOKENS)
        }

        headers = {
            "Authorization": f"Bearer {VLLM_API_KEY}",
            "Content-Type": "application/json",
        }

        r = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        r.raise_for_status()

        data = r.json()
        return data["choices"][0]["message"]["content"].strip()


# =========================
# ROUTER
# =========================

def _get_provider():
    if LLM_BACKEND == "ollama":
        return OllamaProvider()

    if LLM_BACKEND == "vllm":
        return VLLMProvider()

    raise ValueError(f"Backend IA inconnu : {LLM_BACKEND}")


# =========================
# CALL PRINCIPAL
# =========================

def call_llm(messages, temp=0.3, max_tokens=None):
    try:
        provider = _get_provider()
        return provider.generate(
            messages=messages,
            temp=temp,
            max_tokens=max_tokens
        )

    except Exception as e:
        return f"Erreur IA : {str(e)}"


# =========================
# COMPAT
# =========================

def call_ollama(messages, temp=0.3, max_tokens=None):
    return call_llm(messages, temp=temp, max_tokens=max_tokens)