
from core.tools.base import BaseTool
import os
import glob
from pathlib import Path

class RecentFilesTool(BaseTool):
    name = "recent_files"
    description = "Scans for recently modified files in a directory. Params: {'path': '.', 'limit': 10}"
    
    def run(self, params: dict) -> list:
        path = params.get("path", ".")
        limit = int(params.get("limit", 10))
        
        try:
            # Expand ~
            if path.startswith("~"):
                path = os.path.expanduser(path)
                
            p = Path(path)
            if not p.exists():
                return f"Path {path} does not exist."
                
            files = []
            # Scan top level or walk? "Scans for recently modified files" usually implies deep or shallow.
            # Let's do a 1-level deep scan first for speed, or os.walk with depth limit?
            # Let's simple glob for now.
            
            # Using os.scandir for better perf
            entries = []
            with os.scandir(path) as it:
                for entry in it:
                     if entry.is_file():
                         entries.append(entry)
            
            # Sort by mtime DESC
            entries.sort(key=lambda e: e.stat().st_mtime, reverse=True)
            
            top_files = entries[:limit]
            return [e.name for e in top_files]
            
        except Exception as e:
            return f"Error scanning files: {e}"
