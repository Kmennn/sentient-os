
import time
import argparse
import requests
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args()

    print(f"Checking Ollama Latency ({args.runs} runs)...")
    url = "http://localhost:8000/v1/chat/completions" # Using Brain API to proxy or direct?
    # User said "Ollama model load & inference".
    # Brain wraps Local Engine.
    # We should test Brain API latency since that's what matters.
    # POST /v1/chat
    
    api_url = "http://localhost:8000/v1/chat"
    payload = {"message": "Hello, are you ready?", "stream": False}
    
    total_time = 0
    success = 0
    
    for i in range(args.runs):
        start = time.time()
        try:
            resp = requests.post(api_url, json=payload, timeout=30)
            if resp.status_code == 200:
                dur = time.time() - start
                print(f"Run {i+1}: {dur:.4f}s")
                total_time += dur
                success += 1
            else:
                print(f"Run {i+1}: Failed ({resp.status_code})")
        except Exception as e:
            print(f"Run {i+1}: Error {e}")
            
    if success > 0:
        print(f"Avg Latency: {total_time/success:.4f}s")
    else:
        print("All runs failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
