import os
import sys

# Ensure project root (where `src` lives) is on sys.path for tests
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
