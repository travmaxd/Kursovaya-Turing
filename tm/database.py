import sqlite3
from datetime import datetime
import os


DB_PATH = os.path.join(os.path.dirname(__file__), "../turing.db")


def init_db():
    """Создаёт таблицу, если её ещё нет."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            is_palindrome INTEGER NOT NULL,
            steps_count INTEGER,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_result(word: str, is_palindrome: bool, steps_count: int):
    """Сохраняет результат проверки слова."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO history (word, is_palindrome, steps_count, created_at) VALUES (?, ?, ?, ?)",
        (word, int(is_palindrome), steps_count, datetime.now().isoformat(timespec='seconds'))
    )
    conn.commit()
    conn.close()


def get_history(limit: int = 20):
    """Возвращает последние N записей истории."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT word, is_palindrome, steps_count, created_at FROM history ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "word": r[0],
            "is_palindrome": bool(r[1]),
            "steps": r[2],
            "created_at": r[3]
        }
        for r in rows
    ]
