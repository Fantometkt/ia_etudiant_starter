import os
import requests
from providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self):
        self.url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
        self.model = os.getenv("OLLAMA_MODEL", "gemma3")
        self.timeout = float(os.getenv("LLM_REQUEST_TIMEOUT", "180"))

    def generate(self, messages, temperature=0.3, max_tokens=None):
        options = {
            "temperature": temperature
        }

        if max_tokens:
            options["num_predict"] = int(max_tokens)

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": options
        }

        response = requests.post(
            self.url,
            json=payload,
            timeout=self.timeout
        )

        response.raise_for_status()

        return response.json().get("message", {}).get("content", "").strip()