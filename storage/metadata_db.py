import sqlite3
from pathlib import Path
from typing import Any

DB_FILE = "metadata.db"

class MetadataDB:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    storage_path TEXT NOT NULL,
                    content_summary TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    document_id INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    chunk_summary TEXT,
                    chunk_index INTEGER NOT NULL,
                    vector_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def add_document(self, user_id: int, filename: str, storage_path: str, content_summary: str | None = None) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO documents (user_id, filename, storage_path, content_summary) VALUES (?, ?, ?, ?)",
                (user_id, filename, storage_path, content_summary),
            )
            conn.commit()
            return cursor.lastrowid

    def get_user_documents(self, user_id: int) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, filename, storage_path, content_summary, uploaded_at FROM documents WHERE user_id = ? ORDER BY uploaded_at DESC",
                (user_id,),
            ).fetchall()
            return [
                {
                    "id": row[0],
                    "filename": row[1],
                    "storage_path": row[2],
                    "content_summary": row[3],
                    "uploaded_at": row[4],
                }
                for row in rows
            ]

    def add_chunk(self, user_id: int, document_id: int, chunk_text: str, chunk_summary: str | None, chunk_index: int) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO chunks (user_id, document_id, chunk_text, chunk_summary, chunk_index) VALUES (?, ?, ?, ?, ?)",
                (user_id, document_id, chunk_text, chunk_summary, chunk_index),
            )
            chunk_id = cursor.lastrowid
            conn.execute(
                "UPDATE chunks SET vector_id = ? WHERE id = ?",
                (chunk_id, chunk_id),
            )
            conn.commit()
            return chunk_id

    def get_chunks_for_user(self, user_id: int, limit: int | None = None) -> list[dict[str, Any]]:
        query = "SELECT id, document_id, chunk_text, chunk_summary, chunk_index FROM chunks WHERE user_id = ? ORDER BY chunk_index"
        if limit:
            query += f" LIMIT {limit}"
        with self._connect() as conn:
            rows = conn.execute(query, (user_id,)).fetchall()
            return [
                {
                    "id": row[0],
                    "document_id": row[1],
                    "chunk_text": row[2],
                    "chunk_summary": row[3],
                    "chunk_index": row[4],
                }
                for row in rows
            ]

    def clear_user_data(self, user_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM chunks WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM documents WHERE user_id = ?", (user_id,))
            conn.commit()
