"""SQLite storage for Phiversity: render jobs, chat threads, and the
lecture index — one local database file (default <root>/phiversity.db).

What moves into the database:
  jobs      every generation job: status, stage, progress, logs, result
            (previously in-memory and lost on every restart)
  chats     saved conversation threads (previously loose chats/*.json)
  lectures  an index of the generated lectures, refreshed from their
            manifest.json files so listings and search are fast and
            restart-proof

The lecture mp4s and their manifest.json files remain on disk as the
real render artifacts; the database is the queryable record of them.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id       TEXT PRIMARY KEY,
    created  REAL NOT NULL,
    status   TEXT NOT NULL,
    stage    TEXT NOT NULL DEFAULT '-',
    progress INTEGER NOT NULL DEFAULT 0,
    title    TEXT NOT NULL DEFAULT '',
    question TEXT NOT NULL DEFAULT '',
    topic    TEXT NOT NULL DEFAULT '',
    video    TEXT NOT NULL DEFAULT '',
    error    TEXT NOT NULL DEFAULT '',
    logs     TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS chats (
    id       TEXT PRIMARY KEY,
    title    TEXT NOT NULL DEFAULT '',
    modified REAL NOT NULL,
    messages TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS lectures (
    slug              TEXT PRIMARY KEY,
    title             TEXT NOT NULL DEFAULT '',
    question          TEXT,
    format            TEXT,
    preset            TEXT,
    segments          INTEGER NOT NULL DEFAULT 0,
    narration_seconds REAL NOT NULL DEFAULT 0,
    modified          REAL NOT NULL DEFAULT 0,
    video             TEXT NOT NULL DEFAULT ''
);
"""

SQLITE_MAGIC = b"SQLite format 3\x00"


def is_sqlite_file(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return handle.read(16) == SQLITE_MAGIC
    except OSError:
        return False


class Database:
    """Thread-safe SQLite wrapper used by the render server."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        with self.lock:
            self.conn = sqlite3.connect(str(self.path),
                                        check_same_thread=False)
            self.conn.executescript(SCHEMA)
            self.conn.commit()

    def close(self) -> None:
        with self.lock:
            self.conn.close()

    # ------------------------------------------------------------- jobs

    def save_job(self, record: dict) -> None:
        with self.lock:
            self.conn.execute(
                """INSERT INTO jobs (id, created, status, stage, progress,
                   title, question, topic, video, error, logs)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET
                     status=excluded.status, stage=excluded.stage,
                     progress=excluded.progress, title=excluded.title,
                     question=excluded.question, topic=excluded.topic,
                     video=excluded.video, error=excluded.error,
                     logs=excluded.logs""",
                (record["id"], record["created"], record["status"],
                 record.get("stage", "-"), int(record.get("progress", 0)),
                 record.get("title", ""), record.get("question", ""),
                 record.get("topic", ""), record.get("video", ""),
                 record.get("error", ""),
                 json.dumps(record.get("logs", [])[-400:])))
            self.conn.commit()

    def load_jobs(self) -> list:
        with self.lock:
            rows = self.conn.execute(
                """SELECT id, created, status, stage, progress, title,
                   question, topic, video, error, logs
                   FROM jobs ORDER BY created""").fetchall()
        records = []
        for row in rows:
            records.append({"id": row[0], "created": row[1],
                            "status": row[2], "stage": row[3],
                            "progress": row[4], "title": row[5],
                            "question": row[6], "topic": row[7],
                            "video": row[8], "error": row[9],
                            "logs": _load_json(row[10], [])})
        return records

    # ------------------------------------------------------------ chats

    def save_chat(self, chat_id: str, title: str, messages: list,
                  modified: float | None = None) -> bool:
        if not isinstance(messages, list):
            return False
        messages = [m for m in messages if isinstance(m, dict)][:300]
        with self.lock:
            self.conn.execute(
                """INSERT INTO chats (id, title, modified, messages)
                   VALUES (?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET
                     title=excluded.title, modified=excluded.modified,
                     messages=excluded.messages""",
                (chat_id, title[:80], modified or time.time(),
                 json.dumps(messages)))
            self.conn.commit()
        return True

    def load_chat(self, chat_id: str) -> dict | None:
        with self.lock:
            row = self.conn.execute(
                """SELECT title, modified, messages FROM chats
                   WHERE id=?""", (chat_id,)).fetchone()
        if not row:
            return None
        return {"id": chat_id, "title": row[0],
                "modified": row[1], "messages": _load_json(row[2], [])}

    def chat_ids(self) -> list:
        with self.lock:
            return [row[0] for row in
                    self.conn.execute("SELECT id FROM chats").fetchall()]

    def list_chats(self) -> list:
        with self.lock:
            rows = self.conn.execute(
                """SELECT id, title, modified, messages FROM chats
                   ORDER BY modified DESC""").fetchall()
        out = []
        for chat_id, title, modified, messages in rows:
            msgs = _load_json(messages, [])
            out.append({"id": chat_id, "title": title or "Untitled chat",
                        "modified": modified, "messages": msgs})
        return out

    def delete_chat(self, chat_id: str) -> bool:
        with self.lock:
            cursor = self.conn.execute("DELETE FROM chats WHERE id=?",
                                       (chat_id,))
            self.conn.commit()
        return cursor.rowcount > 0

    # --------------------------------------------------------- lectures

    def upsert_lecture(self, record: dict) -> None:
        with self.lock:
            self.conn.execute(
                """INSERT INTO lectures (slug, title, question, format,
                   preset, segments, narration_seconds, modified, video)
                   VALUES (?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(slug) DO UPDATE SET
                     title=excluded.title, question=excluded.question,
                     format=excluded.format, preset=excluded.preset,
                     segments=excluded.segments,
                     narration_seconds=excluded.narration_seconds,
                     modified=excluded.modified, video=excluded.video""",
                (record["slug"], record["title"], record["question"],
                 record["format"], record["preset"],
                 int(record["segments"]), float(record["narration_seconds"]),
                 float(record["modified"]), record["video"]))
            self.conn.commit()

    def delete_lecture(self, slug: str) -> None:
        with self.lock:
            self.conn.execute("DELETE FROM lectures WHERE slug=?", (slug,))
            self.conn.commit()

    def list_lectures(self) -> list:
        with self.lock:
            rows = self.conn.execute(
                """SELECT slug, title, question, format, preset, segments,
                   narration_seconds, modified, video FROM lectures
                   ORDER BY modified DESC""").fetchall()
        return [{"slug": r[0], "title": r[1], "question": r[2],
                 "format": r[3], "preset": r[4], "segments": r[5],
                 "narration_seconds": r[6], "modified": r[7],
                 "video": r[8]} for r in rows]


def _load_json(text: str, default):
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return default
