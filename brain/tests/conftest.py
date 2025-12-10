import sys
import os
import pytest

# Add brain and root to path globally for all tests
current_dir = os.path.dirname(os.path.abspath(__file__))
brain_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(brain_dir)

if brain_dir not in sys.path:
    sys.path.insert(0, brain_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
