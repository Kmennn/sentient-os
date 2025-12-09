
from core.tools.base import BaseTool
import psutil
import datetime
import platform

class SystemInfoTool(BaseTool):
    name = "system_info"
    description = "Returns CPU, RAM, Uptime, and OS details."
    
    def run(self, params: dict) -> dict:
        try:
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot_time
            
            info = {
                "os": platform.platform(),
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "ram_percent": psutil.virtual_memory().percent,
                "uptime": str(uptime).split('.')[0],
                "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else "N/A"
            }
            return info
        except Exception as e:
            return f"Error fetching system info: {e}"
