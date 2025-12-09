
from core.tools.registry import BaseTool
import sqlite3
import shutil
import os
import tempfile
import glob

class WebInfoTool(BaseTool):
    @property
    def name(self):
        return "web_info"
    
    @property
    def description(self):
        return "Search local Chrome history. Params: 'query' (str), 'limit' (int)."
    
    @property
    def category(self):
        return "web"

    def run(self, params):
        query = params.get("query", "")
        limit = int(params.get("limit", 10))
        
        # Locate History DB
        # Windows default
        base = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\History")
        if not os.path.exists(base):
             # Try finding generic
             return "Chrome History not found at default location."
        
        # Copy to temp
        try:
            tmp = tempfile.mktemp()
            shutil.copy2(base, tmp)
            
            conn = sqlite3.connect(tmp)
            cursor = conn.cursor()
            
            sql = "SELECT url, title, last_visit_time FROM urls WHERE hidden = 0"
            args = []
            if query:
                sql += " AND (title LIKE ? OR url LIKE ?)"
                args = [f"%{query}%", f"%{query}%"]
            
            sql += " ORDER BY last_visit_time DESC LIMIT ?"
            args.append(limit)
            
            cursor.execute(sql, args)
            rows = cursor.fetchall()
            conn.close()
            os.remove(tmp)
            
            results = []
            for r in rows:
                # Convert Chrome time (microseconds since 1601) not implemented for brewity, strict raw
                results.append({"url": r[0], "title": r[1]})
            
            return results
        except Exception as e:
            return f"Error reading history: {e}"
