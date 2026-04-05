from pathlib import Path
import faiss
import numpy as np

VECTOR_DIMENSION = 3072

class VectorStore:
    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.root_path.mkdir(parents=True, exist_ok=True)

    def _user_index_path(self, user_id: int) -> Path:
        user_dir = self.root_path / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir / "index.faiss"

    def _create_index(self) -> faiss.IndexIDMap:
        flat_index = faiss.IndexFlatIP(VECTOR_DIMENSION)
        return faiss.IndexIDMap(flat_index)

    def _ensure_index(self, user_id: int) -> faiss.IndexIDMap:
        index_path = self._user_index_path(user_id)
        if index_path.exists():
            return faiss.read_index(str(index_path))
        index = self._create_index()
        faiss.write_index(index, str(index_path))
        return index

    def add_vectors(self, user_id: int, embeddings: list[list[float]], ids: list[int]) -> None:
        if not embeddings or not ids or len(embeddings) != len(ids):
            return
        index = self._ensure_index(user_id)
        vectors = np.array(embeddings, dtype="float32")
        ids_array = np.array(ids, dtype="int64")
        index.add_with_ids(vectors, ids_array)
        faiss.write_index(index, str(self._user_index_path(user_id)))

    def search(self, user_id: int, query_embedding: list[float], top_k: int = 5) -> list[tuple[int, float]]:
        index_path = self._user_index_path(user_id)
        if not index_path.exists():
            return []
        index = faiss.read_index(str(index_path))
        query_vector = np.array([query_embedding], dtype="float32")
        scores, ids = index.search(query_vector, top_k)
        hits = []
        for vector_id, score in zip(ids[0], scores[0]):
            if vector_id == -1:
                continue
            hits.append((int(vector_id), float(score)))
        return hits

    def reset_index(self, user_id: int) -> None:
        index_path = self._user_index_path(user_id)
        if index_path.exists():
            index_path.unlink()
        self._ensure_index(user_id)
