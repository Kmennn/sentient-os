
import sqlite3
import sys
from pathlib import Path

# Adjust path to find core
sys.path.append(str(Path(__file__).parent.parent))

from core.db import get_connection

def migrate():
    print("Running v1.8 Stability Migration...")
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # WAL Mode
        cursor.execute("PRAGMA journal_mode=WAL;")
        print("- WAL Mode Enabled")
        
        # Add Indexes if missing
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vision_ts ON vision_events(timestamp DESC)")
        print("- Index idx_vision_ts created")
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tools_name_ts ON tool_invocations(tool_name, timestamp DESC)")
        print("- Index idx_tools_name_ts created")
        
        # Cleanup logs older than 30 days (initial cleanup)
        import time
        cutoff = int(time.time()) - (30 * 86400)
        cursor.execute("DELETE FROM agent_logs WHERE timestamp < ?", (cutoff,))
        print(f"- Cleaned up {cursor.rowcount} old agent logs")
        
        conn.commit()
        print("Migration Complete.")
    except Exception as e:
        print(f"Migration Failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
