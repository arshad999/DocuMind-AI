import os
from pathlib import Path
from typing import Any, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set in the environment")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def create_embeddings(self, texts: List[str], model: str = "text-embedding-3-large") -> List[List[float]]:
        response = self.client.embeddings.create(model=model, input=texts)
        return [data.embedding for data in response.data]

    def create_chat_completion(self, messages: List[dict[str, str]], temperature: float = 0.2, max_tokens: int = 1400) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

