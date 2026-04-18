from llm import call_llm

messages = [
    {"role": "user", "content": "Réponds uniquement par: test"}
]

print(call_llm(messages, temp=0.0))
