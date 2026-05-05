from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, messages, temperature=0.3, max_tokens=None):
        pass