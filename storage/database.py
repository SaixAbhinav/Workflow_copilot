import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "history.db")

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                workflow  TEXT NOT NULL,
                input_preview TEXT,
                result    TEXT NOT NULL
            )
        """)

def save_result(workflow: str, input_text: str, result: dict):
    init_db()
    preview = input_text.strip()[:120].replace("\n", " ")
    with _connect() as conn:
        conn.execute(
            "INSERT INTO history (workflow, input_preview, result) VALUES (?, ?, ?)",
            (workflow, preview, json.dumps(result))
        )

def get_history(limit: int = 50) -> list[dict]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, timestamp, workflow, input_preview, result "
            "FROM history ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [
        {
            "id": r["id"],
            "timestamp": r["timestamp"],
            "workflow": r["workflow"],
            "input_preview": r["input_preview"],
            "result": json.loads(r["result"]),
        }
        for r in rows
    ]

def clear_history():
    init_db()
    with _connect() as conn:
        conn.execute("DELETE FROM history")
