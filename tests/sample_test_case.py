from pathlib import Path
from auth.auth import AuthManager
from storage.metadata_db import MetadataDB
from storage.vector_store import VectorStore
from ingestion.chunking import Chunker

BASE_DIR = Path(__file__).resolve().parents[1]
DB_DIR = BASE_DIR / "data" / "db"
VECTOR_DIR = BASE_DIR / "data" / "vector_store"


def test_chunking():
    text = "Section 1\n\nThis is a sample paragraph.\n\nSection 2\n\nThis is another paragraph."
    chunks = Chunker.split_text_into_chunks(text, chunk_size=80, overlap=20)
    assert len(chunks) >= 1
    assert "Section 1" in chunks[0]


def test_auth_flow():
    manager = AuthManager(DB_DIR / "test_auth.db")
    username = "testuser"
    password = "secret123"
    manager.create_user(username, password)
    assert manager.verify_user(username, password)
    assert manager.get_user_id(username) is not None


def test_vector_store_index():
    store = VectorStore(VECTOR_DIR / "test")
    store.reset_index(999)
    embeddings = [[0.01] * 1536, [0.02] * 1536]
    ids = [1001, 1002]
    store.add_vectors(999, embeddings, ids)
    results = store.search(999, embeddings[0], top_k=1)
    assert results and results[0][0] == 1001


if __name__ == "__main__":
    test_chunking()
    test_auth_flow()
    test_vector_store_index()
    print("All sample tests passed.")
