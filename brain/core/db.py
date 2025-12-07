import os
import sqlite3
from typing import Optional
from pathlib import Path

DB_PATH = Path("data/sentient.db")

def get_db_path() -> str:
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return str(DB_PATH)

def get_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database."""
    return sqlite3.connect(get_db_path(), check_same_thread=False)

def init_db():
    """Initializes the database tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp INTEGER NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_ts ON conversations(user_id, timestamp DESC)")

    # Events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            payload JSON,
            timestamp INTEGER NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON events(timestamp DESC)")

    # Action Records
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS action_records (
            action_id TEXT PRIMARY KEY,
            user_id TEXT,
            intent TEXT,
            metadata JSON,
            status TEXT,
            timestamp INTEGER
        )
    """)
    
    # Agent Logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT,
            step TEXT,
            details JSON,
            timestamp INTEGER
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
