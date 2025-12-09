
import sys
import os

# Add parent dir to path to find 'core'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.db import init_db, get_connection

def migrate():
    print("Initializing Database...")
    init_db()
    
    # Future migrations can verify schema version here
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM conversations")
    count = cursor.fetchone()[0]
    print(f"Migration complete. 'conversations' table ready (rows: {count}).")
    conn.close()

if __name__ == "__main__":
    migrate()
