from typing import List
from storage.vector_store import VectorStore
from storage.metadata_db import MetadataDB

class Retriever:
    def __init__(self, vector_store: VectorStore, metadata_db: MetadataDB, embedding_client):
        self.vector_store = vector_store
        self.metadata_db = metadata_db
        self.embedding_client = embedding_client

    def retrieve(self, user_id: int, query: str, top_k: int = 5) -> List[str]:
        query_embedding = self.embedding_client.create_embeddings([query])[0]
        hits = self.vector_store.search(user_id, query_embedding, top_k=top_k)
        if not hits:
            return []

        chunks = []
        with self.metadata_db._connect() as conn:
            for vector_id, _score in hits:
                row = conn.execute(
                    "SELECT chunk_text FROM chunks WHERE vector_id = ? AND user_id = ?",
                    (vector_id, user_id),
                ).fetchone()
                if row:
                    chunks.append(row[0])
        return chunks
