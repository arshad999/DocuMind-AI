from llm.prompts import build_generation_prompt
from llm.openai_client import OpenAIClient

class DocumentGenerator:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client

    def generate_document(self, context_chunks: list[str], request: str, optional_inputs: dict[str, str]) -> str:
        messages = build_generation_prompt(context_chunks, request, optional_inputs)
        response = self.openai_client.create_chat_completion(messages)
        return response
