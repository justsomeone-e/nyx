import sys
import os

# Adjust path so src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from cli import main

if __name__ == "__main__":
    main()
