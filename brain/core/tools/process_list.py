
from core.tools.registry import BaseTool
import psutil

class ProcessListTool(BaseTool):
    @property
    def name(self):
        return "process_list"

    @property
    def description(self):
        return "List top running processes by CPU/Memory. Params: 'limit' (int, default 10), 'sort_by' ('cpu' or 'memory')."
    
    @property
    def category(self):
        return "system"

    def run(self, params):
        limit = int(params.get("limit", 10))
        sort_by = params.get("sort_by", "cpu")
        
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append(p.info)
            except:
                pass
        
        # Sort
        key = 'cpu_percent' if sort_by == 'cpu' else 'memory_percent'
        procs.sort(key=lambda x: x.get(key, 0.0), reverse=True)
        
        top = procs[:limit]
        return top

class DiskUsageTool(BaseTool):
    @property
    def name(self):
        return "disk_usage"

    @property
    def description(self):
        return "Check disk usage. Params: 'path' (default '/')."

    @property
    def category(self):
        return "system"

    def run(self, params):
        import shutil
        path = params.get("path", "C:\\" if psutil.os.name == 'nt' else "/")
        try:
           usage = shutil.disk_usage(path)
           return {
               "total_gb": round(usage.total / (1024**3), 2),
               "used_gb": round(usage.used / (1024**3), 2),
               "free_gb": round(usage.free / (1024**3), 2),
               "percent": round((usage.used / usage.total) * 100, 1)
           }
        except Exception as e:
            return f"Error: {e}"
