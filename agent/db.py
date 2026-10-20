import sqlite3
import datetime
from .config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote TEXT NOT NULL,
            category TEXT,
            caption TEXT,
            image_url TEXT,
            media_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quote_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_text TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comment_replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comment_id TEXT UNIQUE,
            post_id TEXT,
            comment_text TEXT,
            reply_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def is_comment_replied(comment_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM comment_replies WHERE comment_id = ?", (comment_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def record_reply(comment_id: str, post_id: str, comment_text: str, reply_text: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO comment_replies (comment_id, post_id, comment_text, reply_text)
        VALUES (?, ?, ?, ?)
    """, (comment_id, post_id, comment_text, reply_text))
    conn.commit()
    conn.close()

def is_quote_used(quote_text: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM quote_history WHERE LOWER(TRIM(quote_text)) = LOWER(TRIM(?))", (quote_text,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def record_post(quote: str, category: str, caption: str, image_url: str, media_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO posts (quote, category, caption, image_url, media_id)
        VALUES (?, ?, ?, ?, ?)
    """, (quote, category, caption, image_url, media_id))
    cursor.execute("""
        INSERT OR IGNORE INTO quote_history (quote_text)
        VALUES (?)
    """, (quote,))
    conn.commit()
    conn.close()

def get_recent_quotes(limit: int = 20) -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT quote_text FROM quote_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

# Initialize tables immediately
init_db()
