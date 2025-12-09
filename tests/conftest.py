
import sys
import os

# Add brain to path
brain_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../brain"))
if brain_path not in sys.path:
    sys.path.insert(0, brain_path)
