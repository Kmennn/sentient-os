
import sqlite_utils
import sys
import os

# Ensure we are in the right directory
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sentient.db")

def migrate():
    print(f"Migrating database at {DB_PATH} for v1.9...")
    db = sqlite_utils.Database(DB_PATH)

    # 1. Create vision_events table
    if "vision_events" not in db.table_names():
        print("Creating table: vision_events")
        db["vision_events"].create({
            "id": str,                 # PK
            "user_id": str,
            "screenshot_path": str,    # Path to stored screenshot
            "ocr_text": str,           # Raw text extracted
            "tags": str,              # JSON: detected objects/tags
            "timestamp": int
        }, pk="id")
    else:
        print("Table 'vision_events' already exists.")

    # 2. Create tool_invocations table
    if "tool_invocations" not in db.table_names():
        print("Creating table: tool_invocations")
        db["tool_invocations"].create({
            "id": str,                 # PK
            "user_id": str,
            "tool_name": str,
            "params": str,             # JSON inputs
            "result": str,             # JSON output
            "status": str,             # success, error, pending
            "timestamp": int
        }, pk="id")
    else:
        print("Table 'tool_invocations' already exists.")

    print("Migration v1.9 complete.")

if __name__ == "__main__":
    migrate()
