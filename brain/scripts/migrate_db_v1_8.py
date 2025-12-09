
import sqlite_utils
import sys
import os

# Ensure we are in the right directory
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sentient.db")

def migrate():
    print(f"Migrating database at {DB_PATH} for v1.8...")
    db = sqlite_utils.Database(DB_PATH)

    # 1. Create agent_logs table
    if "agent_logs" not in db.table_names():
        print("Creating table: agent_logs")
        db["agent_logs"].create({
            "log_id": int,
            "agent_name": str,
            "step": str,
            "details": str, # JSON as text
            "timestamp": int
        }, pk="log_id")
    else:
        print("Table 'agent_logs' already exists.")

    # 2. Create action_records table
    if "action_records" not in db.table_names():
        print("Creating table: action_records")
        db["action_records"].create({
            "action_id": str,
            "user_id": str,
            "intent": str,
            "metadata": str, # JSON as text
            "status": str,
            "timestamp": int
        }, pk="action_id")
    else:
        print("Table 'action_records' already exists.")

    print("Migration v1.8 complete.")

if __name__ == "__main__":
    migrate()
