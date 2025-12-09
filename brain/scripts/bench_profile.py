
import psutil
import time
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--short", action="store_true")
    args = parser.parse_args()

    print("Sentient OS - Performance Baseline")
    print("----------------------------------")
    
    cpu_start = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    
    print(f"CPU Usage: {cpu_start}%")
    print(f"Memory Total: {mem.total / (1024**3):.2f} GB")
    print(f"Memory Used: {mem.used / (1024**3):.2f} GB ({mem.percent}%)")
    
    if args.short:
        sys.exit(0)
        
    # Extended check (simulated)
    print("Monitoring for 5s...")
    for _ in range(5):
        time.sleep(1)
        print(f"CPU: {psutil.cpu_percent()}%")

if __name__ == "__main__":
    main()
