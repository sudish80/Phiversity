import hashlib
import hmac
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "phiversity.db"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_login_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS login_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                login_at TEXT NOT NULL,
                ip TEXT,
                user_agent TEXT,
                success INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        conn.commit()


def _hash_password(password: str, salt: bytes) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return digest.hex()


def create_user(username: str, email: str, password: str):
    now = _utc_now()
    salt = os.urandom(16)
    password_hash = _hash_password(password, salt)

    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (username, email, password_hash, salt, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username.strip(), email.strip().lower(), password_hash, salt.hex(), now, now),
        )
        conn.commit()
        user_id = cur.lastrowid

    return {"id": user_id, "username": username, "email": email, "created_at": now}


def authenticate_user(login: str, password: str, ip: str = "", user_agent: str = ""):
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT id, username, email, password_hash, salt
            FROM users
            WHERE username = ? OR email = ?
            LIMIT 1
            """,
            (login.strip(), login.strip().lower()),
        ).fetchone()

        if not row:
            conn.execute(
                "INSERT INTO login_events (user_id, login_at, ip, user_agent, success) VALUES (?, ?, ?, ?, ?)",
                (None, _utc_now(), ip, user_agent, 0),
            )
            conn.commit()
            return None

        check_hash = _hash_password(password, bytes.fromhex(row["salt"]))
        ok = hmac.compare_digest(check_hash, row["password_hash"])

        conn.execute(
            "INSERT INTO login_events (user_id, login_at, ip, user_agent, success) VALUES (?, ?, ?, ?, ?)",
            (row["id"], _utc_now(), ip, user_agent, 1 if ok else 0),
        )

        if ok:
            conn.execute(
                "UPDATE users SET last_login_at = ?, updated_at = ? WHERE id = ?",
                (_utc_now(), _utc_now(), row["id"]),
            )

        conn.commit()

        if not ok:
            return None

        return {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
        }