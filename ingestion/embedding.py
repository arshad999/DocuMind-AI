from typing import List
from llm.openai_client import OpenAIClient

class EmbeddingEngine:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client

    def embed_chunks(self, texts: List[str]) -> List[List[float]]:
        return self.openai_client.create_embeddings(texts)
