
from core.tools.registry import BaseTool
import os
import glob
from typing import Dict, Any

class FileSearchTool(BaseTool):
    name = "file_search"
    description = "Searches for files by pattern in a specific directory."

    def run(self, params: Dict[str, Any]) -> str:
        root_path = params.get("path", ".")
        query = params.get("query", "") # Unused in walk logic but maybe used for filename match
        pattern = params.get("pattern", "*") 
        if not query and pattern == "*": pattern = "*"
        elif query and pattern == "*": pattern = f"*{query}*"
        
        max_depth = params.get("max_depth", 3)
        ignore_dirs = {".git", "node_modules", "__pycache__", ".venv", ".idea", ".vscode"}
        
        matches = []
        try:
            start_depth = root_path.rstrip(os.path.sep).count(os.path.sep)
            
            import fnmatch
            
            for root, dirs, files in os.walk(root_path):
                # Depth limit check
                current_depth = root.rstrip(os.path.sep).count(os.path.sep)
                if current_depth - start_depth > max_depth:
                    dirs[:] = [] # Don't recurse further
                    continue
                
                # Prune ignored
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                
                # Search files
                for filename in files:
                    if fnmatch.fnmatch(filename, pattern):
                        matches.append(os.path.join(root, filename))
                        if len(matches) >= 50:
                            return str(matches) # Limit return size
                            
            return str(matches)
        except Exception as e:
            return f"Error searching files: {e}"
