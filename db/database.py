# db/database.py
import sqlite3
from datetime import datetime

DB_PATH = "bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS messages;")  # ❗удалит старые данные

    cursor.execute("""
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            chat_id INTEGER,
            text TEXT,
            reply_to_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()

def save_message(user_id: int, chat_id: int, text: str, reply_to_text: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO messages (user_id, chat_id, text, reply_to_text, timestamp) VALUES (?, ?, ?, ?, ?)",
        (user_id, chat_id, text, reply_to_text, datetime.utcnow())
    )

    cursor.execute("""
        DELETE FROM messages
        WHERE id NOT IN (
            SELECT id FROM messages
            ORDER BY timestamp DESC
            LIMIT 50
        );
    """)
    conn.commit()
    conn.close()

def get_last_messages(chat_id: int, limit: int = 50) -> list[str]:
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT text FROM messages
        WHERE chat_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (chat_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in reversed(rows)]  # чтобы были от старых к новым