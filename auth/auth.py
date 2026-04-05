import hashlib
import os
import sqlite3
import secrets
from pathlib import Path

DB_FILENAME = "auth.db"

class AuthManager:
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
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def _hash_password(self, password: str, salt: str) -> str:
        raw = password.encode("utf-8")
        key = hashlib.pbkdf2_hmac("sha256", raw, salt.encode("utf-8"), 200_000)
        return key.hex()

    def create_user(self, username: str, password: str) -> bool:
        if not username or not password:
            return False
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                    (username.strip().lower(), password_hash, salt),
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username: str, password: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT password_hash, salt FROM users WHERE username = ?",
                (username.strip().lower(),),
            ).fetchone()
            if not row:
                return False
            stored_hash, salt = row
            return self._hash_password(password, salt) == stored_hash

    def get_user_id(self, username: str) -> int | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id FROM users WHERE username = ?",
                (username.strip().lower(),),
            ).fetchone()
            return row[0] if row else None
