import httpx
import json

BASE_URL = "http://localhost:8000/v1"

def test_tools():
    # 1. List
    resp = httpx.get(f"{BASE_URL}/tools")
    print("Tools List:", resp.json())
    
    # 2. Calculator
    resp = httpx.post(f"{BASE_URL}/tools/run", json={"tool": "calculator", "params": {"expression": "10 + 5 * 2"}})
    print("Calc Result:", resp.json())
    
    # 3. File Search (test ignore)
    resp = httpx.post(f"{BASE_URL}/tools/run", json={"tool": "file_search", "params": {"path": ".", "query": "kernel.py", "max_depth": 3}})
    print("File Search Result:", resp.json())

if __name__ == "__main__":
    test_tools()
