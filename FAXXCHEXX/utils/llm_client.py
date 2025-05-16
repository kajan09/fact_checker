# utils/llm_client.py

import json
import requests

class LocalLLMClient:

    # HELP ME JOHANNES!!!!!!!!!!!!!!!
    def __init__(self, endpoint: str = "http://localhost:8000/v1/chat/completions"):
        self.endpoint = endpoint

    def __call__(self, *, prompt: str, temperature: float, max_tokens: int) -> dict | str:
        payload = {
            "model": "your-model-name",
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        resp = requests.post(self.endpoint, json=payload)
        resp.raise_for_status()

        data = resp.json()  # assume your server returns {"choices":[{"text": "..."}]}
        text = data["choices"][0]["text"]

        # Try to parse as JSON; if it fails, return raw text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
